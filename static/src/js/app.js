var get_template = function (template_name) {
    var tpl = document.getElementById(template_name).innerText;
    return tpl;
};

Vue.component('pronunciation', {
    delimiters: ['[[', ']]'],
    props: ["id", "src", "best"],
    data: function () {
        return {
            already_playing: false
        }
    },
    template: get_template("audio-template"),
    methods: {
        play: function () {
            var audio_el = document.getElementById(this.id);
            audio_el.play();
            this.$emit('sound-playing', this.id);
        }
    }
});


var vue_app = new Vue({
    el: "#learning_states",
    delimiters: ['[[', ']]'],
    data: {
        words: [{
                id: 1,
                value: "abandon",
                is_user_know_meaning: false,
                is_user_know_pronunciation: false,
                meanings: [
                    {
                        id: 1,
                        value: "Cease to support or look after (someone)",
                    },
                    {
                        id: 2,
                        value: "Give up completely (a practice or a course of action)",
                    }
                ],
                audio: [
                    {
                        id: "audio_1",
                        src: "/static/build/audio/abandon.mp3",
                        best: true
                    },
                    {
                        id: "audio_2",
                        src: "/static/build/audio/abandon_2.mp3",
                        best: false
                    }
                ],
                ui: {
                    show_meanings: false,
                    want_another_audio: false
                }
            }
        ],
    },
    methods: {
        on_sound_play: function (word, audio_id) {
            word.ui.want_another_audio = true;
        }
    }
});