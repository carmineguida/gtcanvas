################################################################################
# grader.py - Originally coded by: Carmine T. Guida
################################################################################

import sys
import requests
import csv

################################################################################

base = "https://gatech.instructure.com"

token = ""
course = ""
assignment = ""

canvasProfile = {}
canvasCourses = []
canvasCourseUsers = []
canvasCourseAssignments = []
courseAssignmentSubmissions = []

################################################################################

def CanvasAPIGet(url):
    global base
    global token
    global perPage

    pageNum = 1

    headers = {"Authorization": "Bearer " + token}

    current = base + url
    responseList = []

    while True:
        params = {"page":str(pageNum), "per_page":"100"}
        response = requests.get(current, headers=headers, params=params)

        if (response.status_code != requests.codes.ok):
            print("ERROR HTTP STATUS CODE: " + str(response.status_code))
            quit()
        else:
            result = response.json()
            if (isinstance(result, dict)):
                return result
            responseList.extend(result)
            linkCurrent = response.links["current"]
            linkLast = response.links["last"]

            if (linkCurrent["url"] == linkLast["url"]):
                return responseList
            pageNum += 1


def CanvasAPIPut(url, params):
    global base
    global token
    global perPage

    headers = {"Authorization": "Bearer " + token}

    response = requests.put(base + url, headers=headers, params=params)

    if (response.status_code != requests.codes.ok):
        print("ERROR HTTP STATUS CODE: " + str(response.status_code))
    else:
        #print (response.text)
        return response.json()

################################################################################

def GetProfile():
    global canvasProfile
    canvasProfile = CanvasAPIGet("/api/v1/users/self/profile")

def GetCourses():
    global canvasCourses
    canvasCourses = CanvasAPIGet("/api/v1/courses")

def GetCourseUsers():
    global canvasCourseUsers
    global course
    canvasCourseUsers = CanvasAPIGet("/api/v1/courses/" + course + "/users")

def GetCourseAssignments():
    global canvasCourseAssignments
    global course
    canvasCourseAssignments = CanvasAPIGet("/api/v1/courses/" + course + "/assignments")

def GetCourseAssignmentSubmissions():
    global courseAssignmentSubmissions
    global course
    global assignment
    courseAssignmentSubmissions = CanvasAPIGet("/api/v1/courses/" + course + "/assignments/" + assignment + "/submissions")

def SubmitGrade(course_id, assignment_id, user_id, score, comment):
    params = {
        "include[visibility]":"true",
        "submission[posted_grade]":score,
        "comment[text_comment]":comment
    }

    CanvasAPIPut("/api/v1/courses/" + course_id + "/assignments/" + assignment_id + "/submissions/" + user_id, params)

################################################################################

def FindSubmissionByUser(user):
    user_id = user["id"]
    for entry in courseAssignmentSubmissions:
        if (entry["user_id"] == user_id):
            return entry
    return None

################################################################################

def PromptToken():
    global token
    print("What is your Canvas Token?")
    print("Found in: Canvas > Account > Settings > Approved Integrations: > New Access Token.")
    while len(token) <= 0:
        token = str(input(":")).strip()

def PromptCourse():
    global canvasCourses
    global course
    print("Which Course?")
    for entry in canvasCourses:
        print(str(entry["id"]) + " " + entry["name"])

    while len(course) <= 0:
        course = str(input(":")).strip()

def PromptAssignment():
    global canvasCourseAssignments
    global assignment
    print("Which Assignment?")
    for entry in canvasCourseAssignments:
        print(str(entry["id"]) + " " + entry["name"])

    while len(assignment) <= 0:
        assignment = str(input(":")).strip()

def ProcessMenuOption(option):
    pos = option.find(" ")
    if (pos > 0):
        command = option[:pos].strip().lower()
        filename = option[pos:].strip()

        if (command == "quit" or command == "exit"):
            quit()

        if (command == "export"):
            CommandExport(filename)
            quit()

        if (command == "import"):
            CommandImport(filename)
            quit()

def PromptMenu():
    print("What would you like to do?")
    print("> export filename.csv")
    print("> import filename.csv")

    option = ""

    if (len(sys.argv) >= 3):
        option = sys.argv[2]

    if (len(sys.argv) >= 4):
        option += " " + sys.argv[3]

    if (option != ""):
        ProcessMenuOption(option)
        quit()

    while True:
        option = ""
        while len(option) <= 0:
            option = str(input(":")).strip()
        ProcessMenuOption(option)

################################################################################

def GetAttachmentsLink(attachments):
    if (attachments == None):
        return ""
    link = ""
    for attachment in attachments:
        if (link != ""):
            link += "\n"
        link += attachment["url"]
    return link

def GetCourseAndAssignment():
    GetCourses()
    PromptCourse()

    GetCourseUsers()
    GetCourseAssignments()
    PromptAssignment()

    GetCourseAssignmentSubmissions()

def CommandExport(filename):
    global canvasCourseUsers
    global course
    global assignment

    GetCourseAndAssignment()

    print ("Exporting: " + filename)
    headerList =  ["course_id", "assignment_id", "user_id", "name", "link", "score", "comment"];

    with open(filename, "w")  as csvfile:

        writer = csv.writer(csvfile, dialect="excel")
        writer.writerow(headerList)
        for user in canvasCourseUsers:
            link = ""
            score = ""
            comment = ""

            submission = FindSubmissionByUser(user)
            if (submission != None):
                if ("score" in submission):
                    if (submission["score"] != None):
                        score = submission["score"]
                if ("attachments" in submission):
                    link = GetAttachmentsLink(submission["attachments"])

            row = [course, assignment, user["id"], user["sortable_name"], link, score, comment]
            writer.writerow(row)

    print("Done!")

def IndexRequired(list, id, errorIfMissing=True):
    try:
        return list.index(id)
    except ValueError:
        if (errorIfMissing):
            print("ERROR Could not find column: " + id)
            quit()
        return -1


def CommandImport(filename):
    print ("Importing: " + filename)
    with open(filename, "r")  as csvfile:
        reader = csv.reader(csvfile)
        headerList = next(reader)

        course_id_index = IndexRequired(headerList, "course_id")
        assignment_id_index = IndexRequired(headerList, "assignment_id")
        user_id_index = IndexRequired(headerList, "user_id")
        score_index = IndexRequired(headerList, "score")
        comment_index = IndexRequired(headerList, "comment")

        name_index = IndexRequired(headerList, "name", False)
        if (name_index < 0):
            name_index = IndexRequired(headerList, "Name", False)

        rowCount = 1
        for row in reader:
            course_id = row[course_id_index]
            assignment_id = row[assignment_id_index]
            user_id = row[user_id_index]
            score = row[score_index]
            comment = row[comment_index]
            name = ""

            if (name_index >= 0):
                name = row[name_index]

            print("Processing Row " + str(rowCount) + " " + user_id + " " + name + ": ", end="")

            if (len(score) <= 0):
                print("Skipped (score was blank)")
            else:
                SubmitGrade(course_id, assignment_id, user_id, score, comment)
                print("Grade posted")
            rowCount += 1

    print("Done!")


################################################################################

def main():
    global token
    if (len(sys.argv) >= 2):
        token = sys.argv[1]
    else:
        PromptToken()

    GetProfile()
    print("Hello, " + canvasProfile["name"])
    PromptMenu()



################################################################################

main()
