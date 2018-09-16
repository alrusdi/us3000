var vue_app = new Vue({
    el: "#learning_states",
    delimiters: ['[[', ']]'],
    data: {
        message: "HW!",
        words: [{
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
        ]
    },
    methods: {
        play_audio: function (audio_id) {
            document.getElementById(audio_id).play()
        }
    }
});