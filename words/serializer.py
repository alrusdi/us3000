from django.conf import settings


def serialize_learning_state(learning_state):
    '''
    {
        id: 1,
        value: "abandon",
        is_user_know_meaning: false,
        is_user_know_pronunciation: false,
        meanings: [
            "Cease to support or look after (someone); desert",
            "Give up completely (a practice or a course of action)",
            "(abandon oneself to) Allow oneself to indulge in (a desire or impulse)"
        ],
        audio: [
            {
                id: "audio_1",
                src: "/static/build/audio/abandon.mp3"
            }
        ],
        ui: {
            show_meanings: false,
        }
    }
    '''
    serialized_word = dict(
        id=learning_state.pk,
        value=learning_state.word.value,
        spelling=learning_state.word.spelling,
        is_user_know_meaning=learning_state.is_user_know_meaning,
        is_user_know_pronunciation=learning_state.is_user_know_pronunciation,
        meanings=[],
        audio=[],
        ui={
            "show_meanings": False,
            "meaning_server_call": False,
            "pronunciation_server_call": False,
        }
    )
    for p in learning_state.get_pronunciations():
        audio = {
            "id": "audio_{}".format(p['id']),
            'by': p['by'],
            'sex': p['sex'],
            "src": p['src'],
            "best": p['best']
        }
        serialized_word['audio'].append(audio)

    for m in learning_state.word.meaning_set.all():
        serialized_word['meanings'].append({
            "id": "meaning_{}".format(m.pk),
            "value": m.value
        })
    return serialized_word
