# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from os.path import join, exists, basename
from glob import glob
import re
import time

from behave import given, when, then

from mycroft.messagebus import Message
from mycroft.audio import wait_while_speaking


TIMEOUT = 10


def find_dialog(skill_path, dialog):
    """Check the usual location for dialogs.

    TODO: subfolders
    """
    if exists(join(skill_path, 'dialog')):
        return join(skill_path, 'dialog', 'en-us', dialog)
    else:
        return join(skill_path, 'locale', 'en-us', dialog)


def load_dialog_file(dialog_path):
    """Load dialog files and get the contents."""
    with open(dialog_path) as f:
        lines = f.readlines()
    return [l.strip().lower() for l in lines
            if l.strip() != '' and l.strip()[0] != '#']


def load_dialog_list(skill_path, dialog):
    """Load dialog from files into a single list.

    Arguments:
        skill (MycroftSkill): skill to load dialog from
        dialog (list): Dialog names (str) to load

    Returns:
        tuple (list of Expanded dialog strings, debug string)
    """
    dialog_path = find_dialog(skill_path, dialog)

    debug = 'Opening {}\n'.format(dialog_path)
    return load_dialog_file(dialog_path), debug


def dialog_from_sentence(sentence, skill_path):
    """Find dialog file from example sentence."""
    dialog_paths = join(skill_path, 'dialog', 'en-us', '*.dialog')
    best = (None, 0)
    for path in glob(dialog_paths):
        patterns = load_dialog_file(path)
        match, _ = _match_dialog_patterns(patterns, sentence.lower())
        if match is not False:
            if len(patterns[match]) > best[1]:
                best = (path, len(patterns[match]))
    if best[0] is not None:
        return basename(best[0])
    else:
        return None


def _match_dialog_patterns(dialogs, sentence):
    """Match sentence against a list of dialog patterns.

    Returns index of found match.
    """
    # Allow custom fields to be anything
    d = [re.sub(r'{.*?\}', r'.*', t) for t in dialogs]
    # Remove left over '}'
    d = [re.sub(r'\}', r'', t) for t in d]
    d = [re.sub(r' .* ', r' .*', t) for t in d]
    # Merge consequtive .*'s into a single .*
    d = [re.sub(r'\.\*( \.\*)+', r'.*', t) for t in d]
    # Remove double whitespaces
    d = ['^' + ' '.join(t.split()) for t in d]
    debug = 'MATCHING: {}\n'.format(sentence)
    for i, r in enumerate(d):
        match = re.match(r, sentence)
        debug += '---------------\n'
        debug += '{} {}\n'.format(r, match is not None)
        if match:
            return i, debug
    else:
        return False, debug


def match_dialog_patterns(dialogs, sentence):
    """Match sentence against a list of dialog patterns.

    Returns simple True/False and not index
    """
    index, debug = _match_dialog_patterns(dialogs, sentence)
    return index is not False, debug


def expected_dialog_check(utterance, skill_path, dialog):
    """Check that expected dialog file is used. """
    dialogs, load_debug = load_dialog_list(skill_path, dialog)
    match, match_debug = match_dialog_patterns(dialogs, utterance)
    return match, load_debug + match_debug


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


def then_timeout(then_func, context, timeout=TIMEOUT):
    count = 0
    debug = ''
    while count < TIMEOUT:
        for message in context.speak_messages:
            status, test_dbg = then_func(message)
            debug += test_dbg
            if status:
                context.matched_message = message
                return True, debug
        time.sleep(1)
        count += 1
    # Timed out return debug from test
    return False, debug


@then('"{skill}" should reply with dialog from "{dialog}"')
def then_dialog(context, skill, dialog):
    skill_path = context.msm.find_skill(skill).path

    def check_dialog(message):
        utt = message.data['utterance'].lower()
        return expected_dialog_check(utt, skill_path, dialog)

    passed, debug = then_timeout(check_dialog, context)
    if not passed:
        print(debug)
    assert passed


@then('"{skill}" should reply with "{example}"')
def then_example(context, skill, example):
    skill_path = context.msm.find_skill(skill).path
    dialog = dialog_from_sentence(example, skill_path)
    print('Matching with the dialog file: {}'.format(dialog))
    assert dialog is not None
    then_dialog(context, skill, dialog)


@then('"{skill}" should reply with anything')
def then_anything(context, skill):
    def check_any_messages(message):
        return (True, '') if message else (False, '')

    passed = then_timeout(check_any_messages, context)
    if not passed:
        print('No speech recieved at all.')
    assert passed


@then('"{skill}" should reply with exactly "{text}"')
def then_exactly(context, skill, text):
    def check_exact_match(message):
        utt = message.data['utterance'].lower()
        debug = 'Comparing {} with expected {}\n'.format(utt, text)
        return (True, debug) if utt == text.lower() else (False, debug)

    passed, debug = then_timeout(check_exact_match, context)
    if not passed:
        print(debug)
    assert passed


@then('mycroft reply should contain "{text}"')
def then_contains(context, text):
    def check_contains(message):
        utt = message.data['utterance'].lower()
        debug = 'Checking if "{}" contains "{}"\n'.format(utt, text)
        return (True, debug) if text.lower() in utt else (False, debug)

    passed, debug = then_timeout(check_contains, context)

    if not passed:
        print('No speech contained the expected content')
    assert passed


@then('the user says "{text}"')
def when_impl(context, text):
    time.sleep(2)
    wait_while_speaking()
    context.bus.emit(Message('recognizer_loop:utterance',
                             data={'utterances': [text],
                                   'lang': 'en-us',
                                   'session': '',
                                   'ident': time.time()},
                             context={'client_name': 'mycroft_listener'}))
