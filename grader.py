################################################################################
# grader.py - Originally coded by: Carmine T. Guida
################################################################################

import os
import sys
import requests
import csv
import urllib
import time

################################################################################

base = "https://gatech.instructure.com"

token = ""
course = ""
assignment = ""
quiz = ""
courseGroup = ""


canvasProfile = {}
canvasCourses = []
canvasCourseUsers = []
canvasCourseAssignments = []
canvasCourseQuizes = []
canvasCourseQuizSubmissions = []
courseAssignmentSubmissions = []
courseGroupCategories = []
courseGroups = []
courseGroupUsers = []

################################################################################

def CanvasAPIGet(url):
    global base
    global token
    global perPage

    pageNum = 1

    headers = {"Authorization": "Bearer " + token}

    current = url
    if (current.startswith(base) == False):
        current = base + url
    responseList = []

    while True:
        params = {"page":str(pageNum), "per_page":"100"}
        response = requests.get(current, headers=headers, params=params)

        if (response.status_code != requests.codes.ok):
            print("ERROR HTTP STATUS CODE: " + str(response.status_code))
            quit()
        else:
            #print("")
            #print("[" + current + "]")
            #print (response.text)
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

    response = requests.put(base + url, headers=headers, data=params)

    if (response.status_code != requests.codes.ok):
        print("ERROR HTTP STATUS CODE: " + str(response.status_code))
    else:
        #print (response.text)
        return response.json()

def CanvasAPIPost(url, params):
    global base
    global token
    global perPage

    headers = {"Authorization": "Bearer " + token}

    response = requests.post(base + url, headers=headers, data=params)

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

def GetCourseGroupCategories():
    global courseGroupCategories
    global course
    courseGroupCategories = CanvasAPIGet("/api/v1/courses/" + course + "/group_categories")

def GetCourseGroups():
    global courseGroups
    global course
    courseGroups = CanvasAPIGet("/api/v1/courses/" + course + "/groups")

def GetCourseGroupUsers():
    global courseGroupUsers
    global courseGroup
    global course
    courseGroupUsers = CanvasAPIGet("/api/v1/groups/" + courseGroup + "/users")

def GetCourseAssignments():
    global canvasCourseAssignments
    global course
    canvasCourseAssignments = CanvasAPIGet("/api/v1/courses/" + course + "/assignments")

def GetCourseQuizes():
    global canvasCourseQuizes
    global course
    canvasCourseQuizes = CanvasAPIGet("/api/v1/courses/" + course + "/quizzes")

def GetCourseQuizSubmissions():
    global canvasCourseQuizes
    global canvasCourseQuizSubmissions
    global course
    global quiz
    canvasCourseQuizSubmissions = CanvasAPIGet("/api/v1/courses/" + course + "/quizzes/" + quiz + "/submissions")


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
    global courseAssignmentSubmissions
    user_id = user["id"]
    for entry in courseAssignmentSubmissions:
        if (entry["user_id"] == user_id):
            return entry
    return None

def FindUser(user_id):
    global canvasCourseUsers
    for entry in canvasCourseUsers:
        if (int(entry["id"]) == int(user_id)):
            return entry
    return None

def FindQuiz(quiz_id):
    global canvasCourseQuizes
    for entry in canvasCourseQuizes:
        if (int(entry["id"]) == int(quiz_id)):
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

def PromptQuiz():
    global canvasCourseQuizes
    global quiz
    print("Which Quiz?")
    for entry in canvasCourseQuizes:
        print(str(entry["id"]) + " " + entry["title"])

    while len(quiz) <= 0:
        quiz = str(input(":")).strip()

def PromptGroup():
    global courseGroups
    global courseGroup
    print("Which Group?")
    for entry in courseGroups:
        print(str(entry["id"]) + " " + entry["name"])

    while len(courseGroup) <= 0:
        courseGroup = str(input(":")).strip()


def ProcessMenuOption(option):
    pos = option.find(" ")
    if (pos < 0):
        pos = len(option)

    command = option[:pos].strip().lower()
    filename = option[pos:].strip()

    if (command == "quit" or command == "exit"):
        quit()

    if (command == "export"):
        CommandExport(filename)
        quit()

    if (command == "getrubric"):
        CommandGetRubric(filename)
        quit()

    if (command == "import"):
        CommandImport(filename)
        quit()

    if (command == "importrubric"):
        CommandImportRubric(filename)
        quit()

    if (command == "download"):
        CommandDownload(filename)
        quit()

    if (command == "exportquiz"):
        CommandExportQuiz(filename)
        quit()

    if (command == "mentor"):
        CommandMentor()
        quit()

def PromptMenu():
    print("What would you like to do?")
    print("> export filename.csv")
    print("> exportquiz filename.csv")
    print("> getrubric filename.csv")
    print("> import filename.csv")
    print("> importrubric filename.csv")
    print("> download folder_to_put_files_in")
    print("> mentor")

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

def GetCourseAndAssignment(excludeSubmissions = False):
    GetCourses()
    PromptCourse()

    GetCourseUsers()

    GetCourseGroupCategories()
    GetCourseGroups()

    GetCourseAssignments()
    PromptAssignment()

    if not excludeSubmissions:
        GetCourseAssignmentSubmissions()

def GetCourseAndQuiz():
    GetCourses()
    PromptCourse()

    GetCourseUsers()

    GetCourseGroupCategories()
    GetCourseGroups()

    GetCourseQuizes()
    PromptQuiz()


def CommandMentor():
    global canvasCourseUsers
    global course

    GetCourses()
    PromptCourse()

    GetCourseUsers()

    GetCourseGroupCategories()
    GetCourseGroups()

    PromptGroup()
    GetCourseGroupUsers()

    mentorName = canvasProfile["name"]

    for user in courseGroupUsers:
        print(mentorName + " - " + user["name"] + " - Mentor Discussion thread")

    print("Done!")


def CommandDownload(foldername):
    global canvasCourseUsers
    global course
    global assignment

    GetCourseAndAssignment()
    PromptGroup()
    GetCourseGroupUsers()

    if (foldername.endswith("/") == False):
        foldername = foldername + "/"

    if (os.path.exists(foldername) == False):
        print("Creating folder: " + foldername)
        os.makedirs(foldername)

    print ("Downloading to: " + foldername)

    for user in courseGroupUsers:
        link = ""

        submission = FindSubmissionByUser(user)
        if (submission != None):
            if ("attachments" in submission):
                attachments = submission["attachments"]
                if (attachments is None):
                    continue

                attachmentCount = 0
                for attachment in attachments:
                    link = attachment["url"]
                    if (link == ""):
                        continue

                    filename = user["sortable_name"]
                    filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    if (attachmentCount > 0):
                        filename = filename + "_" + str(attachmentCount)
                    filename = foldername + filename + ".pdf"

                    print("Downloading: " + link + " [to] " + filename)

                    DownloadURLToFile(link, filename)

                    attachmentCount = attachmentCount + 1

    print("Done!")

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

def ExtractAnswers(events):
    answers = {}
    eventlist = events["quiz_submission_events"]

    for event in eventlist:
        event_type = event["event_type"]
        if (event_type != "question_answered"):
            continue
        event_data = event["event_data"]
        for subevent in event_data:
            quiz_question_id = str(subevent["quiz_question_id"])
            answer = subevent["answer"]
            if (answer == None):
                answer = ""
            else:
                answer = str(answer)

        answers[quiz_question_id] = answer

    return answers


def CommandExportQuiz(filename):
    global canvasCourseQuizes
    global course
    global quiz

    GetCourseAndQuiz()
    GetCourseQuizSubmissions()

    submissionList = canvasCourseQuizSubmissions["quiz_submissions"]

    questionCount = 0
    quizData = FindQuiz(quiz)

    if (quizData != None):
        questionCount = quizData["question_count"]

    print ("Exporting: " + filename + " (" + str(questionCount) + " questions in quiz)")

    #params = {
    #    "quiz_report[report_type]":"student_analysis" #
    #}

    #print ("Telling canvas to generate the report.")
    #report = CanvasAPIPost("/api/v1/courses/" + str(course) + "/quizzes/" + str(quiz)+ "/reports", params)
    #reportURL = report["url"]

    #print ("Sleeping for 10 second to give it time to do that.")
    #time.sleep(10)



    headerList =  ["course_id", "quiz_id", "user_id", "name", "score"];

    for i in range(0, questionCount):
        headerList.append("Q" + str(i + 1) + "Score")

    for i in range(0, questionCount):
        headerList.append("Q" + str(i + 1) + "Answer")

    with open(filename, "w")  as csvfile:
        writer = csv.writer(csvfile, dialect="excel")
        writer.writerow(headerList)

        for submission in submissionList:
            id = submission["id"]
            user_id = submission["user_id"]
            score = submission["score"]

            name = ""
            user = FindUser(user_id)
            if (user != None):
                name = user["sortable_name"]

            correctList = []
            for i in range(0, questionCount):
                correctList.append(0)

            events = CanvasAPIGet("/api/v1/courses/" + str(course) + "/quizzes/" + str(quiz) + "/submissions/" + str(id) + "/events")
            answerdict = ExtractAnswers(events)

            submissionData = CanvasAPIGet("/api/v1/quiz_submissions/" + str(id)+ "/questions")

            answerList = []
            for i in range(0, questionCount):
                answerList.append("")

            submissionQuestions = submissionData["quiz_submission_questions"]
            for entry in submissionQuestions:
                if ("position" not in entry):
                    continue

                position = (entry["position"] - 1)

                if ("correct" in entry):
                    correct = entry["correct"]
                    if (correct == True):
                        correctList[position] = 1

                entry_id = str(entry["id"])
                answer = ""
                if (entry_id in answerdict):
                    answer = answerdict[entry_id]

                #Multiple choice answers are id numbers NOT A, B, C, D so we need to match them up
                if (answer != "" and ("answers" in entry)):
                    answers = entry["answers"]

                    for a in range(0, len(answers)):
                        ans = answers[a]
                        if (str(ans["id"]) == answer):
                            answer = chr(65 + a)
                            break

                answerList[position] = answer

            row = [course, quiz, user_id, name, score]
            for i in range(0, questionCount):
                row.append(correctList[i])

            for i in range(0, questionCount):
                row.append(answerList[i])

            writer.writerow(row)

    print("Done!")

def CommandGetRubric(filename):
    global canvasCourseUsers
    global course
    global assignment

    GetCourseAndAssignment(True)

    global course
    global assignment
    courseAssignnment = CanvasAPIGet("/api/v1/courses/" + course + "/assignments/" + assignment)
    rubric = courseAssignnment["rubric"]


    print ("Exporting: " + filename)
    headerList =  ["course_id", "assignment_id", "rubric_id", "description", "long_description", "points"];

    with open(filename, "w")  as csvfile:

        writer = csv.writer(csvfile, dialect="excel")
        writer.writerow(headerList)
        for item in rubric:
            row = [course, assignment, item["id"], item["description"], item["long_description"], item["points"]]
            writer.writerow(row)

    print("Done!")

def DownloadURLToFile(url, filename):
    with open(filename, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

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

# follows the standard import headers, but link column must exist (and is not used)
# rubric item ID goes in header cell, starting in the cell AFTER link
# put points scored for that item under the rubric item ID and put the comments in the next column
# must have a pair of these columns for every rubric item you wish to populate
# and they must be the LAST columns in the sheet starting AFTER link column
# you can get the rubric item IDs from the exportrubric command
# SAMPLE HEADERS: course_id	assignment_id, user_id, name, link, _5573, comment, _5397, comment
def CommandImportRubric(filename):
    print ("Importing: " + filename)
    with open(filename, "r")  as csvfile:
        reader = csv.reader(csvfile)
        headerList = next(reader)

        course_id_index = IndexRequired(headerList, "course_id")
        assignment_id_index = IndexRequired(headerList, "assignment_id")
        user_id_index = IndexRequired(headerList, "user_id")
        link_index = IndexRequired(headerList, "link")
        rubric_item_start = link_index + 1

        name_index = IndexRequired(headerList, "name", False)
        if (name_index < 0):
            name_index = IndexRequired(headerList, "Name", False)

        rowCount = 1
        for row in reader:
            course_id = row[course_id_index]
            assignment_id = row[assignment_id_index]
            user_id = row[user_id_index]
            name = ""

            if (name_index >= 0):
                name = row[name_index]

            print("Processing Row " + str(rowCount) + " " + user_id + " " + name + ": ", end="")

            params = {
                "include[visibility]":"true"
            }
            i = rubric_item_start
            while i < len(headerList):
                params["rubric_assessment[" + headerList[i] + "][points]"] = row[i]
                params["rubric_assessment[" + headerList[i] + "][comments]"] = row[i + 1]
                i += 2

            CanvasAPIPut("/api/v1/courses/" + course_id + "/assignments/" + assignment_id + "/submissions/" + user_id, params)
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
