"use strict";

const get_template = function (template_name) {
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


const vue_app = new Vue({
    el: "#learning_states",
    delimiters: ['[[', ']]'],
    data: {
        words: [],
        is_data_loading: true
    },
    methods: {
        on_sound_play: function (word, audio_id) {
            word.ui.want_another_audio = true;
        }
    },
    mounted: function () {
      var vue_app = this;
      this.$nextTick(function () {
        // Make a request for a user with a given ID
        axios.get('/learning-states')
          .then(function (response) {
            console.log(vue_app)

            vue_app.words = response.data.words;
            console.log(response);
          })
          .catch(function (error) {
            // handle error
            console.log(error);
          })
          .then(function () {
            // always executed
            vue_app.is_data_loading = false;
          });

      })
    }
});