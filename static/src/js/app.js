"use strict";

const get_template = function (template_name) {
    var tpl = document.getElementById(template_name).innerText;
    return tpl;
};

Vue.component('pronunciations', {
    delimiters: ['[[', ']]'],
    props: ['items'],
    data: function () {
        return {
            already_playing: false,
            current_audio: false,
            show_more_audio_link: false,
            show_other_sounds_dlg: false
        }
    },
    template: get_template("audio-template"),
    methods: {
        play: function (audio_id) {
            for (var i in this.items) {
                if (this.items[i].id == audio_id) {
                    this.current_audio = this.items[i];
                }
            }
            var audio_el = document.getElementById(audio_id);
            audio_el.play();
            this.$emit('sound-playing', this);
        },
        show_other_audios: function () {
            this.show_more_audio_link = false;
            this.show_other_sounds_dlg = true;
        },
        change_audio: function (audio_id) {
            for (var i in this.items) {
                if (this.items[i].id == audio_id) {
                    this.current_audio.best=false;
                    this.current_audio = this.items[i];
                    this.items[i].best = true;
                    this.play(this.current_audio.id);
                }
            }
        },
        hide_other_audio_dlg: function () {
            this.show_more_audio_link = true;
            this.show_other_sounds_dlg = false;
        }
    },
    mounted: function () {
        for (var i in this.items) {
            if (this.items[i].best) this.current_audio = this.items[i];
        }
        this.show_more_audio_link = this.items.length > 1;
    }
});


const vue_app = new Vue({
    el: "#learning_states",
    delimiters: ['[[', ']]'],
    data: {
        words: [],
        is_data_loading: true,
        is_server_error: false
    },
    methods: {
        on_sound_play: function (audio_component) {
            console.log('Now playing', audio_component.current_audio.id);
            console.log('Now playing', audio_component);
        },
        get_preferred_pron: function (word) {
            var preferred_pron;
            word.audio.forEach(function (audio) {
                if (audio.best)
                {
                    preferred_pron = audio.id.replace('audio_', '');
                }
            });
            return preferred_pron
        },
        set_server_call: function (word, target, value) {
            if (target === 'pronunciation') {
                word.ui.pronunciation_server_call = (value === 1);
            } else {
                word.ui.meaning_server_call = (value === 1);
            }
        },
        set_learning_state: function (word, target, value) {
            var vue_app = this;

            // Block for subsequent server calls
            if (word.ui.meaning_server_call && target === 'meaning') return;
            if (word.ui.pronunciation_server_call && target === 'pronunciation') return;
            vue_app.set_server_call(word, target, 1);

            var preferred_pron = this.get_preferred_pron(word);
            axios.get('change-learning-state/' + target + '/' + word.id + '/' + value + '/' + preferred_pron + '/')
            .then (function (response) {
                if (target === 'pronunciation') {
                    word.is_user_know_pronunciation = (value === 1)
                } else {
                    word.is_user_know_meaning = (value === 1)
                }
            })
            .catch (function (error) {
                // TODO react somehow to server error
            })
            .then (function () {
                vue_app.set_server_call(word, target, 0)
            })
        },
        end_session: function () {
            // TODO make call to server view refresh page
        }
    },
    mounted: function () {
        var vue_app = this;
        this.$nextTick(function () {
            // Make a request for a user with a given ID
            axios.get('/learning-states/')
                .then(function (response) {
                    vue_app.words = response.data.words;
                })
                .catch(function (error) {
                    // handle error
                    vue_app.is_server_error = true;
                })
                .then(function () {
                    // always executed
                    vue_app.is_data_loading = false;
                });

        })
    }
});