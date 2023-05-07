# IMP-Scheduler
# KMeans-Imp.
This project aimed to reduce the time behind the scheduling process for the Integrity Mentorship Program(IMP) at the Academic Integrity Office at UCSD. 

## Table of Contents

- [Installation Requirements](#intallment-requirements)
- [Project Description](#project-description)
- [File Descriptions](#file-descriptions)
- [Usage](#usage)

## Installment Requirements
This program needs Python 3 and the pandas package.

## Project Description

The Integrity Mentorship Program (IMP) at the Academic Integrity Office at UCSD is a program designed to help students facing potential suspension from the university due to academic integrity (AI) violations. Students who successfully complete the program can have their suspension cancelled. However, scheduling meetings between mentors and mentees can be challenging due to the limited availability of both parties and the space constraints of the office. In an attempt to solve this problem I developed this project that aimed to speed up the overall scheduling process so that the coordinators could dedicate all the saved time to other more immenient needs in the program. 

## Algorithm Description
The IMP Scheduler tool uses a scheduling algorithm to automate the process of pairing mentors and mentees based on their availability. The algorithm works by first collecting data on the availability of mentors and mentees in separate CSV files. The mentee CSV file contains data on the availability of students, while the mentor CSV file contains a list of all the mentors working with the office for that quarter. A third CSV file, the schedule CSV file, represents the available space the office has for running meetings that quarter.

Once the CSV files are in place, the algorithm begins by cleaning and organizing the data. It then searches for potential pairs of mentors and mentees based on their availability and updates the schedule CSV file accordingly. The algorithm ensures that the maximum number of meetings are scheduled in the available time slots, while also ensuring that each mentor is assigned an equal number of students.

## File Descriptions

- `IMP Scheduler.ipynb`: This file contains the notebook that the user needs to interact with in order to create the new version of the scheduler. The only things the user really needs to change is the magic number which allows for the user to control the max amount of students each mentor can be assigned.
- `methods.py`: This file contains the code that does the behind the scenes work for constructing the schedule. From organizing and cleaning the data to searching for potential pairs for the students methods contains all the necessary functions for this tool to work.
- 'mentee.csv': A csv file that contains our students as well as their overall availability and potential time conflicts like with their corresponding seminar section time.
- 'mentor.csv': A list of all the mentors that are working with the office for that quarter.
- 'schedule.csv': A csv thats structured in a sort of table that represents the available space the office has for running meetings that quarter. Mentors are asked to sign up for slots that line up with their overall availability and as we encounter students with overlapping schedules we pair them up and update the cell in the schedule.

## Usage

The entire process starts will collecting the data from our mentors and students. First, the students availability is collected through a google form which enquires their overall availability throughout the week. Then we create a empty schedule and ask for the mentors to sign up for X amount of time slots depending on the demand for that specific quarter. These eventually become the basis for our mentee and schedule csv files. Finally, the mentor file is just a list of all the mentors that work with our office that quarter, so it's fairly easy to setup. 

Once these files have been established we can import them into our environment where we have our notebook set up. Once these csv files are in the same directory as our notebook we're pretty much ready to go. The one thing that users should pay attention is the Magic Number since this makes sure that the students are equally assigned among the mentors so that no one mentor gets abnormally more students then the other. After we run all cells in the notebook this will create the extras and finalSchedule csv. The extras csv represents any students we weren't able to accomandate due to things like running out of availability, so the user can track any weird cases where we weren't able to match the student. On the other hand the finalSchedule csv will be an updated version of our initial schedule that contains all the pairs we made during this iteration of the algorithm. The user can now download the finalSchedule csv file and import back into any kind of spreadsheet tool like Google Sheets and be set to go.

It's important to note that students are sometimes assigned to the program in waves, so it's possible that we're assigned more students after we've already scheduled the first wave of students. Thankfully, we can just grab the updated versions of the mentees and schedule and replace their corresponding csv files. Then we can rerun the algorithm and have our schedule reflect our newest addition of the "wave 2" students.



