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


def graphDepartmentTermsByKeyAverage(count, mean, subject_filter):
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
            if year == "2018" and quarter != "Winter":
                continue
            terms.append(term)

            instructor_ratings = {}
            for entry in session.query(core.model.CTEC).filter(core.model.CTEC.report_caesar_subject == subject_filter).filter(core.model.CTEC.report_term == term):

                entry_count = getattr(entry, count)
                entry_mean = getattr(entry, mean)

                if entry_count and entry_mean:
                    instructor = entry.report_caesar_instructor
                    if instructor in instructor_ratings:
                        info = {
                            "count": entry_count,
                            "mean": entry_mean
                        }
                        instructor_ratings[instructor].append(info)
                        instructor_cumulative_ratings[instructor].append(info)
                    else:
                        instructor_ratings[instructor] = [{
                            "count": entry_count,
                            "mean": entry_mean
                        }]
                        instructor_cumulative_ratings[instructor] = [{
                            "count": entry_count,
                            "mean": entry_mean
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

    fig.canvas.set_window_title(mean)
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


def rankProfessorByKeyAverage(count, mean, subject_filter):
    instructor_ratings = {}
    instructor_subjects = {}
    for entry in session.query(core.model.CTEC):
        if subject_filter != None:
            if subject_filter != entry.report_caesar_subject:
                continue

        entry_count = getattr(entry, count)
        entry_mean = getattr(entry, mean)

        if entry_count and entry_mean:
            instructor = entry.report_caesar_instructor
            if instructor in instructor_ratings:
                info = {
                    "count": entry_count,
                    "mean": entry_mean
                }
                ratings = instructor_ratings[instructor]
                ratings.append(info)
                instructor_ratings[instructor] = ratings
            else:
                instructor_ratings[instructor] = [{
                    "count": entry_count,
                    "mean": entry_mean
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


def rankProfessorByKeyTotal(count, mean, subject_filter):
    instructor_ratings = {}
    instructor_subjects = {}
    for entry in session.query(core.model.CTEC):
        if subject_filter != None:
            if subject_filter != entry.report_caesar_subject:
                continue

        entry_count = getattr(entry, count)
        entry_mean = getattr(entry, mean)

        if entry_count and entry_mean:
            instructor = entry.report_caesar_instructor
            if instructor in instructor_ratings:
                info = {
                    "count": entry_count,
                    "mean": entry_mean
                }
                ratings = instructor_ratings[instructor]
                ratings.append(info)
                instructor_ratings[instructor] = ratings
            else:
                instructor_ratings[instructor] = [{
                    "count": entry_count,
                    "mean": entry_mean
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


def update(instructor_ratings, entry, key_mean, key_count):

    key_total = key_mean + "_total"
    instructor = entry.report_caesar_instructor

    entry_count = getattr(entry, key_count)
    entry_mean = getattr(entry, key_mean)

    if entry_count and entry_mean:
        if instructor in instructor_ratings and instructor_ratings[instructor]:
            if key_count in instructor_ratings[instructor]:
                instructor_ratings[instructor][key_total] += entry_mean * entry_count
                instructor_ratings[instructor][key_count] += entry_count
            else:
                instructor_ratings[instructor][key_total] = entry_mean * entry_count
                instructor_ratings[instructor][key_count] = entry_count
        else:
            instructor_ratings[instructor] = {
                key_total: entry_mean * entry_count,
                key_count: entry_count
            }
    if instructor in instructor_ratings:
        return instructor_ratings[instructor]
    else:
        return {}


def createProfessorsTable(subject_filter):
    instructor_ratings = {}
    instructor_subjects = {}

    for entry in session.query(core.model.CTEC):
        if subject_filter != None:
            if subject_filter != entry.report_caesar_subject:
                continue

        instructor = entry.report_caesar_instructor

        instructor_ratings[instructor] = update(instructor_ratings, entry, "course_instruction_rating_mean",
                                                "course_instruction_rating_response_count")
        instructor_ratings[instructor] = update(instructor_ratings, entry, "course_overall_rating_mean",
                                                "course_overall_rating_response_count")
        instructor_ratings[instructor] = update(instructor_ratings, entry, "course_learned_rating_mean",
                                                "course_learned_rating_response_count")
        instructor_ratings[instructor] = update(instructor_ratings, entry, "course_challenging_rating_mean",
                                                "course_challenging_rating_response_count")
        instructor_ratings[instructor] = update(instructor_ratings, entry, "course_interest_rating_mean",
                                                "course_interest_rating_response_count")

        if instructor in instructor_subjects:
            subjects = instructor_subjects[instructor]
            subjects.append(entry.report_caesar_subject)
            instructor_subjects[instructor] = list(set(subjects))
        else:
            instructor_subjects[instructor] = [entry.report_caesar_subject]

    for key, value in instructor_ratings.items():
        dict = {}
        dict["name"] = key
        dict["subjects"] = ", ".join(str(x) for x in instructor_subjects[key])

        response_count = 0

        if "course_instruction_rating_response_count" in value:
            mean_key = "course_instruction_rating_mean"
            key_total = mean_key + "_total"
            count = value["course_instruction_rating_response_count"]
            dict[mean_key] = value[key_total] / count
            if response_count == 0:
                response_count = count

        if "course_overall_rating_response_count" in value:
            mean_key = "course_overall_rating_mean"
            key_total = mean_key + "_total"
            count = value["course_overall_rating_response_count"]
            dict[mean_key] = value[key_total] / count
            if response_count == 0:
                response_count = count

        if "course_learned_rating_response_count" in value:
            mean_key = "course_learned_rating_mean"
            key_total = mean_key + "_total"
            count = value["course_learned_rating_response_count"]
            dict[mean_key] = value[key_total] / count
            if response_count == 0:
                response_count = count

        if "course_challenging_rating_response_count" in value:
            mean_key = "course_challenging_rating_mean"
            key_total = mean_key + "_total"
            count = value["course_challenging_rating_response_count"]
            dict[mean_key] = value[key_total] / count
            if response_count == 0:
                response_count = count

        if "course_interest_rating_response_count" in value:
            mean_key = "course_interest_rating_mean"
            key_total = mean_key + "_total"
            count = value["course_interest_rating_response_count"]
            dict[mean_key] = value[key_total] / count
            if response_count == 0:
                response_count = count

        dict["response_count"] = response_count
        obj = core.model.Instructor(dict)
        try:
            session.add(obj)
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()


if __name__ == '__main__':
    engine = create_engine('sqlite:///' + "CTEC.db")
    core.model.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    # for file_name in glob.glob("./input/*.csv"):
    #     with open(file_name, mode='r', encoding='utf-8') as infile:
    #         reader = csv.DictReader(infile)
    #         for row in reader:
    #             print(row)
    #             obj = core.model.CTEC(row)
    #             try:
    #                 session.add(obj)
    #                 session.commit()
    #             except Exception as e:
    #                 session.rollback()

    # createProfessorsTable(None)

    # graphDepartmentTermsByKeyAverage(
    #     "course_instruction_rating_response_count", "course_instruction_rating_mean", "EECS")

    # graphDepartmentTermsByKeyAverage(
    #     "course_overall_rating_response_count", "course_overall_rating_mean", "EECS")
    #
    # graphDepartmentTermsByKeyAverage(
    #     "course_learned_rating_response_count", "course_learned_rating_mean", "EECS")
    #
    # graphDepartmentTermsByKeyAverage(
    #     "course_challenging_rating_response_count", "course_challenging_rating_mean", "EECS")

    # print("\n================\n\nINSTRUCTION\n")
    # rankProfessorByKeyAverage(
    #     "course_instruction_rating_response_count", "course_instruction_rating_mean", "EECS")
    #
    # print("\n================\n\nOVERALL\n")
    # rankProfessorByKeyAverage(
    #     "course_overall_rating_response_count", "course_overall_rating_mean", "EECS")

    # print("\n================\n\nLEARNED\n")
    # rankProfessorByKeyAverage(
    #     "course_learned_rating_response_count", "course_learned_rating_mean", None)
    #
    # print("\n================\n\nCHALLENGED\n")
    # rankProfessorByKeyAverage(
    #     "course_challenging_rating_response_count", "course_challenging_rating_mean", None)
    # rankProfessorByTotal(None)

    # rankProfessorByKeyTotal("course_instruction_rating_response_count",
    #                         "course_instruction_rating_mean", "EECS")

    ctec_count = 0
    response_count = 0

    for entry in session.query(core.model.CTEC):
        ctec_count += 1
        response_count += entry.report_response_count

    print("\n\nCTECS: " + str(ctec_count))
    print("RESPONSES: " + str(response_count))
