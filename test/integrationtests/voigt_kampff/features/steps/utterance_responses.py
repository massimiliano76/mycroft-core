from os.path import join
import re
import time

from behave import given, when, then

from mycroft.messagebus import Message


TIMEOUT = 10


def load_dialog_list(skill_path, dialog):
    """ Load dialog from files into a single list.

    Args:
        skill (MycroftSkill): skill to load dialog from
        dialog (list): Dialog names (str) to load

    Returns:
        tuple (list of Expanded dialog strings, debug string)
    """
    dialog_path = join(skill_path, 'dialog', 'en-us', dialog)
    debug = 'Opening {}\n'.format(dialog_path)
    with open(dialog_path) as f:
        lines = f.readlines()
    return [l.strip().lower() for l in lines], debug


def expected_dialog_check(utterance, skill_path, dialog):
    # Check that expected dialog file is used
    # Extract dialog texts from skill
    dialogs, debug = load_dialog_list(skill_path, dialog)
    # Allow custom fields to be anything
    d = [re.sub(r'{.*?\}', r'.*', t) for t in dialogs]
    # Remove left over '}'
    d = [re.sub(r'\}', r'', t) for t in d]
    # Merge consequtive .*'s into a single .*
    d = [re.sub(r'\.\*( \.\*)+', r'.*', t) for t in d]
    # Remove double whitespaces
    d = [' '.join(t.split()) for t in d]
    debug += 'MATCHING: {}\n'.format(utterance)
    for r in d:
        match = re.match(r, utterance)
        debug += '---------------\n'
        debug += '{} {}\n'.format(r, match is not None)
        if match:
            return True, debug
    else:
        return False, debug


@given('an english speaking user')
def given_impl(context):
    context.lang = 'en-us'


@when('the user says "{text}"')
def when_impl(context, text):
    context.bus.emit(Message('recognizer_loop:utterance',
                             data={'utterances': [text],
                                   'lang': 'en-us',
                                   'session': '',
                                   'ident': time.time()},
                             context={'client_name': 'mycroft_listener'}))


@then('"{skill}" should reply with dialog from "{dialog}"')
def then_impl(context, skill, dialog):
    skill_path = context.msm.find_skill(skill).path
    count = 0
    passed = False
    while not (passed or count > TIMEOUT):
        for message in context.speak_messages:
            utt = message.data['utterance'].lower()
            status, debug = expected_dialog_check(utt, skill_path, dialog)
            if status:
                passed = True
                context.matched_message = message
                break
        else:
            passed = False
        time.sleep(1)
        count += 1
    if not passed:
        print(debug)
    assert passed
