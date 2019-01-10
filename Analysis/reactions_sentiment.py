from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from textblob import TextBlob
import re
import ctec_model


def clean_reaction(reaction):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A - Za - z0 - 9] +)|([^0-9A-Za-z \t]) | (\w + : \/\/\S+)", " ", reaction).split())


def get_reaction_sentiment(reaction):
    '''
    Utility function to classify sentiment of passed tweet
    using textblob's sentiment method
    '''
    # create TextBlob object of passed tweet text
    analysis = TextBlob(clean_reaction(reaction))
    # set sentiment

    if analysis.sentiment.polarity > 0:
        return 'positive | ' + str(analysis.sentiment.polarity)
    elif analysis.sentiment.polarity == 0:
        return 'neutral | 0'
    else:
        return 'negative | ' + str(analysis.sentiment.polarity)


def course_description(ctec):
    return ctec.report_caesar_subject + " " + ctec.report_caesar_class_number + " (" + ctec.report_caesar_instructor + ", " + ctec.report_term + ") "


def start():
    for entry in session.query(ctec_model.CTEC):
        if "DSGN" != entry.report_caesar_subject:
            continue
        # if "205" != entry.report_caesar_class_number:
        #     continue

        if entry.reactions:

            num = 0
            tot = 0
            for reaction in entry.reactions:
                num += 1
                tot += TextBlob(clean_reaction(reaction)).sentiment.polarity
            tot = tot / len(entry.reactions)

            num = entry.time_spent_3_or_fewer + entry.time_spent_4_to_7 + entry.time_spent_8_to_11 + \
                entry.time_spent_12_to_15 + entry.time_spent_16_to_19 + entry.time_spent_20_or_more
            time = entry.time_spent_3_or_fewer * 0 + entry.time_spent_4_to_7 * 4 + entry.time_spent_8_to_11 * \
                8 + entry.time_spent_12_to_15 * 12 + entry.time_spent_16_to_19 * \
                16 + entry.time_spent_20_or_more * 20
            if num:
                time = time / num
            else:
                time = -1

            demo_count = entry.demographics_class_freshman + entry.demographics_class_sophomore + \
                entry.demographics_class_junior + entry.demographics_class_senior
            demo = entry.demographics_class_freshman + entry.demographics_class_sophomore * \
                2 + entry.demographics_class_junior * 3 + entry.demographics_class_senior * 4
            if demo_count:
                demo = demo / demo_count
            else:
                demo = -1

            print(course_description(entry)
                  + "\n\tresponses: " + str(entry.report_response_count)
                  + "\n\tinstruction: " +
                  str(entry.course_instruction_rating_mean)
                  + "\n\toverall: " + str(entry.course_overall_rating_mean)
                  + "\n\tlearned: " + str(entry.course_learned_rating_mean)
                  + "\n\tchallenging: " +
                  str(entry.course_challenging_rating_mean)
                  + "\n\tinterest: " + str(entry.course_interest_rating_mean)
                  + "\nExtra Analysis"
                  + "\n\tave undergrad degree: " + str(demo)[:4]
                  + "\n\treaction polarity: " + str(tot)[:4]
                  + "\n\ttime spent: " + str(time)[:4] + " to " + str(time + 3)[:4] + "\n\n==============")


if __name__ == '__main__':
    engine = create_engine('sqlite:///' + "CTEC.db")
    ctec_model.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    start()
