from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import csv
import os
import core.model
import glob

import math

import matplotlib.ticker as plticker

import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def graphEECSProfessorAverage():
    # [professor] = {
    #     winter 2015: 5,
    #     spring 2016: 10.
    # }
    instructor_term_ratings = {}
    instructor_cumulative_ratings = {}

    years = ["2016", "2017", "2018"]
    quarters = ["Winter", "Spring", "Summer", "Fall"]
    terms = []

    for year in years:
        for quarter in quarters:
            term = quarter + " " + year
            terms.append(term)

            instructor_ratings = {}
            for entry in session.query(core.model.CTEC).filter(core.model.CTEC.report_caesar_subject == "EECS").filter(core.model.CTEC.report_term == term):
                if entry.course_instruction_rating_response_count and entry.course_instruction_rating_mean:
                    instructor = entry.report_caesar_instructor
                    if instructor in instructor_ratings:
                        info = {
                            "count": entry.course_instruction_rating_response_count,
                            "mean": entry.course_instruction_rating_mean
                        }
                        instructor_ratings[instructor].append(info)
                        instructor_cumulative_ratings[instructor].append(info)
                    else:
                        instructor_ratings[instructor] = [{
                            "count": entry.course_instruction_rating_response_count,
                            "mean": entry.course_instruction_rating_mean
                        }]
                        instructor_cumulative_ratings[instructor] = [{
                            "count": entry.course_instruction_rating_response_count,
                            "mean": entry.course_instruction_rating_mean
                        }]

            for key, value in instructor_ratings.items():
                rating_count = 0
                rating_value = 0.0
                for class_rating in value:
                    rating_count += class_rating["count"]
                    rating_value += class_rating["mean"] * \
                        class_rating["count"]

                average = rating_value / rating_count
                if key in instructor_term_ratings:
                    instructor_term_ratings[key][term] = average
                else:
                    instructor_term_ratings[key] = {
                        term: average
                    }

    valid_professors = list(instructor_term_ratings.keys())

    for term in terms:
        filtered_professors = []
        for prof in valid_professors:
            filtered_professors.append(prof)
            if term not in instructor_term_ratings[prof]:
                # filtered_professors.append(prof)
                instructor_term_ratings[prof][term] = float('nan')
        valid_professors = filtered_professors

    condensed_instructor_ratings = {}
    for key, value in instructor_cumulative_ratings.items():
        rating_count = 0
        rating_value = 0.0
        for class_rating in value:
            rating_count += class_rating["count"]
            rating_value += class_rating["mean"] * class_rating["count"]

        condensed_instructor_ratings[key] = rating_value / rating_count

    fig = plt.figure(0)

    fig.canvas.set_window_title("Winter 2015 - Fall 2017")
    size = math.ceil(math.sqrt(len(valid_professors)))

    for index, professor in enumerate(sorted(valid_professors)):
        plt.subplot(size, size, 1 + index)
        plt.title(professor, fontsize=6)

        ax = plt.gca()
        ax.set_facecolor((0.95, 0.95, 0.95))
        fig.patch.set_facecolor((0.95, 0.95, 0.95))

        ratings = []
        abb_terms = []

        for term in terms:
            split_term = term.split(" ")
            if split_term[0] == "Spring":
                abb_terms.append("SG" + split_term[1][2:])
            else:
                abb_terms.append(split_term[0][:1] + split_term[1][2:])

            ratings.append(instructor_term_ratings[professor][term])

        ax.set_xticklabels(abb_terms, rotation=60, fontsize=6)
        plt.plot(terms, ratings, marker='o', color='b')

        major_ticks = np.arange(0, 7, 2)

        ax.set_yticks(major_ticks)
        ax.set_ylim([2, 7])

        # Or if you want different settings for the grids:
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)

        average = [condensed_instructor_ratings[professor]
                   for i in range(len(terms))]
        ax.plot(terms, average, linestyle='--', color='g')

    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95,
                        wspace=0.4, hspace=0.9)
    plt.show()

    # cleaned_data_x = []
    # cleaned_data_y = []
    # for year in years:
    #     for quarter in quarters:
    #         term = quarter + " " + year
    #         cleaned_data_x.append(term)

    # plt.figure(figsize=(8, 6), dpi=80)


def rankProfessorByAverage():
    instructor_ratings = {}
    instructor_subjects = {}
    for entry in session.query(core.model.CTEC):
        if entry.course_instruction_rating_response_count and entry.course_instruction_rating_mean:
            instructor = entry.report_caesar_instructor
            if instructor in instructor_ratings:
                info = {
                    "count": entry.course_instruction_rating_response_count,
                    "mean": entry.course_instruction_rating_mean
                }
                ratings = instructor_ratings[instructor]
                ratings.append(info)
                instructor_ratings[instructor] = ratings
            else:
                instructor_ratings[instructor] = [{
                    "count": entry.course_instruction_rating_response_count,
                    "mean": entry.course_instruction_rating_mean
                }]

            if instructor in instructor_subjects:
                subjects = instructor_subjects[instructor]
                subjects.append(entry.report_caesar_subject)
                instructor_subjects[instructor] = list(set(subjects))
            else:
                instructor_subjects[instructor] = [entry.report_caesar_subject]

    condensed_instructor_ratings = {}
    condensed_instructor_ratings_count = {}
    for key, value in instructor_ratings.items():
        rating_count = 0
        rating_value = 0.0
        for class_rating in value:
            rating_count += class_rating["count"]
            rating_value += class_rating["mean"] * class_rating["count"]

        condensed_instructor_ratings[key] = rating_value / rating_count
        condensed_instructor_ratings_count[key] = rating_count

    last_rank = 1
    last_rank_value = 6.0
    raw_rank = 0

    for key in reversed(sorted(condensed_instructor_ratings,
                               key=lambda k: (condensed_instructor_ratings[k], condensed_instructor_ratings_count[k]))):
        raw_rank += 1

        rating = "{0:.3f}".format(condensed_instructor_ratings[key])
        rank = None
        if rating == last_rank_value:
            rank = last_rank
        else:
            last_rank_value = rating
            last_rank = raw_rank
            rank = last_rank

        print(str(rank) + ". " + key + ": " + rating + " (N: " + str(
            condensed_instructor_ratings_count[key]) + ") (S: " + ", ".join(str(x) for x in instructor_subjects[key]) + ")")
    #


def rankProfessorByTotal():
    instructor_ratings = {}
    instructor_subjects = {}
    for entry in session.query(core.model.CTEC):
        if entry.course_instruction_rating_response_count and entry.course_instruction_rating_mean:
            instructor = entry.report_caesar_instructor
            if instructor in instructor_ratings:
                info = {
                    "count": entry.course_instruction_rating_response_count,
                    "mean": entry.course_instruction_rating_mean
                }
                ratings = instructor_ratings[instructor]
                ratings.append(info)
                instructor_ratings[instructor] = ratings
            else:
                instructor_ratings[instructor] = [{
                    "count": entry.course_instruction_rating_response_count,
                    "mean": entry.course_instruction_rating_mean
                }]

            if instructor in instructor_subjects:
                subjects = instructor_subjects[instructor]
                subjects.append(entry.report_caesar_subject)
                instructor_subjects[instructor] = list(set(subjects))
            else:
                instructor_subjects[instructor] = [entry.report_caesar_subject]

    condensed_instructor_ratings = {}
    condensed_instructor_ratings_count = {}
    for key, value in instructor_ratings.items():
        rating_count = 0
        rating_value = 0.0
        for class_rating in value:
            rating_count += class_rating["count"]
            rating_value += class_rating["mean"] * class_rating["count"]

        condensed_instructor_ratings[key] = rating_value
        condensed_instructor_ratings_count[key] = rating_count

    last_rank = 1
    last_rank_value = 6.0
    raw_rank = 0

    # s = sorted(s, key = lambda x: (x[1], x[2]))

    for key in reversed(sorted(condensed_instructor_ratings,
                               key=lambda k: (condensed_instructor_ratings[k], condensed_instructor_ratings_count[k]))):
        raw_rank += 1

        rating = "{0:.3f}".format(condensed_instructor_ratings[key])
        rank = None
        if rating == last_rank_value:
            rank = last_rank
        else:
            last_rank_value = rating
            last_rank = raw_rank
            rank = last_rank

        average = "{0:.3f}".format(
            condensed_instructor_ratings[key] / condensed_instructor_ratings_count[key])

        print(str(rank) + ". " + key + ": " + rating + " (N: " + str(
            condensed_instructor_ratings_count[key]) + ") (A: " + average + ") (S: " + ", ".join(str(x) for x in instructor_subjects[key]) + ")")


if __name__ == '__main__':

    # os.remove("CTEC.db")
    engine = create_engine(
        'sqlite:///' + "CTEC.db")

    core.model.CTEC.metadata.bind = engine
    core.model.CTEC.metadata.create_all()

    session = sessionmaker(bind=engine)()

    #
    # for file_name in glob.glob("./input/*.csv"):
    #     with open(file_name, mode='r', encoding='utf-8') as infile:
    #         reader = csv.DictReader(infile)
    #         for row in reader:
    #             if row["report_caesar_instructor"] != "Borislava Miltcheva" and "Advanced Conceptual Workshop" not in row["report_caesar_title"]:
    #                 obj = core.model.CTEC(row)
    #                 try:
    #                     session.add(obj)
    #                     session.commit()
    #                 except Exception as e:
    #                     print(row)
    #                     print(e)
    #                     print()
    #                     session.rollback()

    rankByAverage()
    # graphEECSProfessorAverage()

    count = 0

    for entry in session.query(core.model.CTEC):
        count += entry.report_response_count

    print(count)

    # park_filtered_attraction_ids = []
    # for attraction_id in attraction_ids:
    #     facility = session.query(core.model.Facility).filter(
    #         core.model.Facility.id == attraction_id).first()
    #     if facility:
    #         if filter_park:
    #             if filter_park == facility.location_theme_park_id:
    #                 attraction_ids_names[attraction_id] = facility.name
    #                 park_filtered_attraction_ids.append(attraction_id)
    #             else:
    #                 print("Filter: Wrong park - " + facility.name)
    #         else:
    #             attraction_ids_names[attraction_id] = facility.name
    #             park_filtered_attraction_ids.append(attraction_id)
    #     else:
    #         attraction_ids_names[attraction_id] = attraction_id
    #         park_filtered_attraction_ids.append(attraction_id)
    #
    # sorted_attraction_ids = sorted(
    #     attraction_ids_names, key=lambda k: attraction_ids_names[k])
    #
    # final_attraction_ids = []
    # if filter_none:
    #     for attraction_id in park_filtered_attraction_ids:
    #         had_wait_times = False
    #         for time_key in entries.keys():
    #             if attraction_id in entries[time_key]:
    #                 wait = entries[time_key][attraction_id].posted_minutes
    #                 if wait:
    #                     had_wait_times = True
    #                     break
    #
    #         if had_wait_times:
    #             final_attraction_ids.append(attraction_id)
    #         else:
    #             print("Filter: No wait times - " +
    #                   attraction_ids_names[attraction_id])
    # else:
    #     final_attraction_ids = sorted_attraction_ids
    #
    # # Headers
    # delimiter = "\t"
    # csv_string = date + delimiter
    # for attraction_id in final_attraction_ids:
    #     csv_string += attraction_ids_names[attraction_id] + delimiter
    # csv_string = csv_string[:-len(delimiter)]
    # csv_string += "\n"
    #
    # wrote_first_line = False
    # for time_key in entries.keys():
    #
    #     times_string = ""
    #     valid_wait_time = False
    #     for attraction_id in final_attraction_ids:
    #         if attraction_id in entries[time_key]:
    #             wait = entries[time_key][attraction_id].posted_minutes
    #             if wait:
    #                 times_string += str(wait) + delimiter
    #                 valid_wait_time = True
    #             else:
    #                 times_string += delimiter
    #         else:
    #             times_string += delimiter
    #
    #     if not wrote_first_line and not valid_wait_time:
    #         print("Filter: Skipping first time with no wait - " + time_key)
    #         continue
    #
    #     csv_string += time_key + delimiter
    #     csv_string = csv_string + times_string[:-len(delimiter)]
    #     csv_string += "\n"
    #     wrote_first_line = True
    #
    # print("Saving results from " + str(len(final_attraction_ids)) + " attractions")
    # with open("output/" + date + ".csv", "w") as text_file:
    #     text_file.write(csv_string)

# posted_minutes
