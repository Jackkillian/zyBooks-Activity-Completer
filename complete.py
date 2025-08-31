from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import os
from dotenv import load_dotenv

def get_base_url():
    url = os.getenv("COURSE_URL")
    if not url.endswith("/"):
        url += "/"
    return url

def nav_to_section(driver, ch, sec):
    driver.get(f"{get_base_url()}chapter/{ch}/section/{sec}")
    WebDriverWait(driver, 10).until(
        expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, ".zb-card.zybook-section")
        )
    )

def complete_all(driver):
    try:
        playAnimations(driver)
        completeCustomInteractions(driver)
        completeMultipleChoice(driver)
        completeShortAnswer(driver)
        completeMatching(driver)
        # completeSelectionProblems(driver)
    except Exception as err:
        print(f"GOT ERR COMPLETING PARTICIPATION: {err}")

def checkCompleted(activity):
    if skip_completed:
        try:
            activity.find_element_by_css_selector(
                "div.zb-chevron.check.title-bar-chevron.orange.filled.large")
            return True
        except NoSuchElementException:
            return False
    return False

# WORKS
def playAnimations(driver):
    # TODO: Play all animations at once
    print("finding animations")
    animation_players = driver.find_elements(By.CLASS_NAME, "animation-canvas")
    
    print(f"FOUND {len(animation_players)} ANIMATIONS")

    for animation in animation_players:
        if checkCompleted(animation):
            print("Skipping completed animation activity")
            continue
        # crumbs = driver.find_element_by_css_selector("li.bread-crumb")
        start = driver.find_element_by_css_selector("div.section-header-row")
        driver.execute_script("arguments[0].click();",
                              start)  # Switched to JavaScript clicking for this because of above crumbs that seemingly can't be hidden or clicked around.
        double_speed = animation.find_element_by_css_selector("div.speed-control")
        double_speed.click()
        start_button = animation.find_element(By.CLASS_NAME, "animation-controls").find_element(By.CLASS_NAME, "start-button")
        start_button.click()
        while (True):
            if (animation.find_elements_by_xpath(".//div[@class='pause-button']")):
                continue
            try:
                play_button = animation.find_element_by_css_selector("div.play-button.bounce")
                play_button.click()
            except:
                pass
            if (animation.find_elements_by_css_selector("div.play-button.rotate-180")):
                break
        print("Completed animation activity")

# WORKS
def completeCustomInteractions(driver):
    custom_activties = driver.find_elements(By.CSS_SELECTOR, ".content-tool-content-resource.interactive-activity-container.participation")

    print(f"FOUND {len(custom_activties)} CUSTOM ACTIVITIES")

    for activity in custom_activties:
        if checkCompleted(activity):
            print("Skipping completed interactive activity")
            continue

        driver.find_element_by_xpath("//div[@class='section-header-row']").click()

        buttons = activity.find_element(By.CSS_SELECTOR, ".activity-payload").find_elements_by_xpath(".//button")
        for button in buttons:
            button.click()

# WORKS
def completeMultipleChoice(driver):
    multiple_choice_sets = driver.find_elements(By.CLASS_NAME, "multiple-choice-payload")

    print(f"FOUND {len(multiple_choice_sets)} MULT CHOICE")

    for question_set in multiple_choice_sets:
        if checkCompleted(question_set):
            print("Skipping completed multiple choice activity")
            continue

        driver.find_element_by_xpath("//div[@class='section-header-row']").click()
        questions = question_set.find_elements(By.XPATH, ".//div[@class='question-set-question multiple-choice-question ']")

        print(f"FOUND {len(questions)} QUESTIONS")
        for question in questions:
            # Go through each choice, check if correct box pops up
            choices = question.find_elements(By.XPATH, ".//label")
            print(f"FOUND {len(choices)} CHOICES")

            # print(dir(choices[0]))

            for choice in choices:
                choice.click()

                element = WebDriverWait(question, 1).until(
                    expected_conditions.visibility_of_element_located(
                        (By.XPATH, ".//h3[text()='Correct' or text()='Incorrect']")
                    )
                )
                print("ELEMENT")
                print(f"{element.text} ({element.tag_name})")

                if element.text == "Correct":
                    print("FOUND CORRECT CHOICE")
                    break # found the right choice

        print("Completed multiple choice set")

# WORKS
def completeShortAnswer(driver):
    short_answer_sets = driver.find_elements(By.CSS_SELECTOR, ".short-answer-content-resource.interactive-activity-container.participation")

    print(f"FOUND {len(short_answer_sets)} SHORT ANSWER SETS")

    for question_set in short_answer_sets:
        if checkCompleted(question_set):
            print("Skipping completed short answer activity")
            continue
        
        questions = question_set.find_elements(By.CSS_SELECTOR, ".question-set-question.short-answer-question")
        
        print(f"FOUND {len(questions)} QUESTIONS IN SET")
        
        for question in questions:
            show_answer_button = question.find_element(By.CSS_SELECTOR, ".zb-button.secondary.show-answer-button")
            show_answer_button.click()
            show_answer_button.click()

            answer = question.find_element(By.CSS_SELECTOR, ".forfeit-answer").text
            text_area = question.find_element(By.CSS_SELECTOR, ".zb-input")

            # print(f"Completing question - answer: {answer}")
            text_area.send_keys(answer)

            check_button = question.find_element(By.CSS_SELECTOR, ".zb-button.primary.raised.check-button")
            check_button.click()

        print("Completed short answer set")

# WORKS - with supervision...
def completeMatching(driver):
    matching_sets = driver.find_elements(By.CSS_SELECTOR, ".custom-content-resource.interactive-activity-container.large.participation")
    matching_sets += driver.find_elements(By.CSS_SELECTOR, ".custom-content-resource.interactive-activity-container.medium.participation")
    matching_sets += driver.find_elements(By.CSS_SELECTOR, ".custom-content-resource.interactive-activity-container.small.participation")

    print(f"FOUND {len(matching_sets)} MATCHING SETS")
    
    for matching in matching_sets:
        # payload = matching.find_elements(By.XPATH, "")

        if checkCompleted(matching):
            print("Skipping completed matching/run activity")
            continue
        try:  # Support for 'run this code' activities, which use same class definition as matching activities. Only works for some code activities, as some require just running while others require editing the code first
            run_button = matching.find_element_by_css_selector("button.run-button.zb-button.primary.raised")
            run_button.click()
            print("Attempted run activity")
            continue
        except NoSuchElementException:
            pass

        matching.click()
        rows = matching.find_elements_by_class_name("definition-row")

        for row in rows:
            print(f"Handling {row.text}")
            while True:
                draggable = matching.find_element(By.CSS_SELECTOR, ".zb-sortable-item.definition-match-term")
                bucket = row.find_element_by_class_name("term-bucket")

                # scroll the bucket into view
                # driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bucket)

                # get center coordinates of draggable and bucket
                # draggable_location = draggable.location_once_scrolled_into_view
                # bucket_location = bucket.location_once_scrolled_into_view

                # print(f"Drag loc {draggable_location}")
                # print(f"Bucket loc {bucket_location}")

                # print(bucket_location['x'] - draggable_location['x'])
                # print(bucket_location['y'] - draggable_location['y'])

                # now perform offset drag
                # action = ActionChains(driver)
                # action \
                #     .move_to_element(draggable).click_and_hold().move_by_offset(
                #     bucket_location['x'] - draggable_location['x'],
                #     bucket_location['y'] - draggable_location['y']
                # ).release().perform()

                action = ActionChains(driver)
                action.move_to_element(bucket).drag_and_drop(draggable, bucket).perform()

                # WebDriverWait(driver, 5).until(expected_conditions.visibility_of(bucket))

                # driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bucket)

                # action = ActionChains(driver)
                # action.click_and_hold(draggable).move_to_element(bucket).release().perform()

                try:
                    WebDriverWait(row, .75).until(lambda driver: row.text.endswith("Correct"))
                    break
                except TimeoutException:
                    pass
        print("Completed matching set")

def completeSelectionProblems(driver):
    selection_problem_sets = driver.find_elements_by_xpath(
        "//div[@class='interactive-activity-container detect-answer-content-resource participation large ember-view']")
    selection_problem_sets += driver.find_elements_by_xpath(
        "//div[@class='interactive-activity-container detect-answer-content-resource participation medium ember-view']")
    selection_problem_sets += driver.find_elements_by_xpath(
        "//div[@class='interactive-activity-container detect-answer-content-resource participation small ember-view']")
    for question_set in selection_problem_sets:
        if checkCompleted(question_set):
            print("Skipping completed selection activity")
            continue
        driver.find_element_by_xpath("//div[@class='section-header-row']").click()
        questions = question_set.find_elements_by_xpath(
            ".//div[@class='question-set-question detect-answer-question ember-view']")
        for question in questions:
            choices = question.find_elements_by_xpath(".//div[@class='unclicked']")
            for choice in choices:
                choice.click()
                if (question.find_elements_by_xpath(".//div[@class='explanation has-explanation correct']")):
                    break
        print("Completed selection problem set")

def completeProgressionChallenges(driver):  # Currently not used
    progression_challenges = driver.find_elements_by_xpath(
        "//div[@class='interactive-activity-container custom-content-resource challenge large ember-view']")
    progression_challenges += driver.find_elements_by_xpath(
        "//div[@class='interactive-activity-container custom-content-resource challenge medium ember-view']")
    progression_challenges += driver.find_elements_by_xpath(
        "//div[@class='interactive-activity-container custom-content-resource challenge small ember-view']")
    for progression in progression_challenges:
        if checkCompleted(progression):
            print("Skipping completed progression activity")
            continue
        progression_status = progression.find_elements_by_xpath(".//div[@class='zyante-progression-status-bar'']/div")
        for status in progression_status:
            if status.text == 1:
                start_button = progression.find_element_by_xpath(
                    ".//button[@class='zyante-progression-start-button button']")
                start_button.click()
            else:
                next_button = progression.find_element_by_xpath("class='zyante-progression-next-button button']")
                next_button.click()
    return

load_dotenv()

geckodriver_path = os.getenv("DRIVER_PATH")
options = Options()
options.headless = False
options.add_argument("-devtools")
skip_completed = False

chapter = int(input("Chapter: "))
std_sections = input("Section(s): ")

if "," in std_sections:
    sections = map(lambda val: int(val.trim()), std_sections.split(","))
elif "-" in std_sections:
    start, end = std_sections.split("-")
    sections = [i for i in range(int(start), int(end) + 1)]
else:
    sections = [int(std_sections)]

fp = webdriver.FirefoxProfile(os.getenv("FIREFOX_PROFILE"))
driver = webdriver.Firefox(firefox_profile=fp, executable_path=geckodriver_path, options=options)

for section in sections:
    print(f"Completing {chapter}.{section}")
    nav_to_section(driver, chapter, section)
    complete_all(driver)
    print("Done!")

input("Press enter to quit...")
driver.quit()
