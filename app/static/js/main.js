Vue.component('input-recording', {
    props: ['metadata'],
    delimiters: ['[[', ']]'],
    template: '<transition name="slide">\
    <li\
    :class="{active: isActive}"\
    @click="activateElement"\
    v-if="show">\
        <div class="metadata isrc">\
            ISRC:\
            <span v-if=\'[[ metadata.rec_isrc ]] != "            "\'>\
                [[ metadata.rec_isrc ]]\
            </span>\
            <span v-else>-</span>\
        </div>\
        <div class="metadata artist">\
            Artist:\
            <span>[[ metadata.rec_artist ]]</span>\
        </div>\
        <div class="metadata title">\
            Title:\
            <span>[[ metadata.rec_title ]]</span>\
        </div>\
        <div class="metadata duration">\
            Duration:\
            <span v-if="[[ metadata.rec_duration ]] != 0">\
                [[ metadata.rec_duration ]]\
            </span>\
            <span v-else>-</span>\
        </div>\
    </li>\
    </transition>',
    data() {
        return {
            isActive: false,
            show: true
        }
    },
    methods: {
        activateElement: function() {
            if (!this.isActive) {
                this.isActive = true;
                this.$emit('get-element-info', this)
            }
        },
        deactivateElement: function() {
            this.isActive = false;
        }
    }
});

Vue.component('candidate-recording', {
    props: ['metadata'],
    delimiters: ['[[', ']]'],
    template: '\
    <li\
    :class="{active: isActive}"\
    @click="activateElement">\
        <div class="metadata similarity" :title="\'Similarity: \' + percentage + \'%\'">\
            <div v-if="percentage >= 80" class="green"></div>\
            <div v-else-if="percentage >= 50" class="yellow"></div>\
            <div v-else class="red"></div>\
        </div>\
        <div class="metadata isrc">\
            ISRC:\
            <span v-if=\'[[ metadata.match_rec_id__isrc ]] != "            "\'>\
                [[ metadata.match_rec_id__isrc ]]\
            </span>\
            <span v-else>-</span>\
        </div>\
        <div class="metadata artist">\
            Artist:\
            <span>[[ metadata.match_rec_id__artist ]]</span>\
        </div>\
        <div class="metadata title">\
            Title:\
            <span>[[ metadata.match_rec_id__title ]]</span>\
        </div>\
        <div class="metadata duration">\
            Duration:\
            <span v-if="[[ metadata.match_rec_id__duration ]] != 0">\
                [[ metadata.match_rec_id__duration ]]\
            </span>\
            <span v-else>-</span>\
        </div>\
    </li>',
    data() {
        return {
            isActive: false,
        }
    },
    computed: {
        percentage() {
            return (this.metadata.score / 250 * 100).toFixed(0);
        } 
    },
    methods: {
        activateElement: function() {
            if (!this.isActive) {
                this.isActive = true;
                this.$emit('select-candidate', this)
            }
        },
        deactivateElement: function() {
            this.isActive = false;
        }
    }
})

var recs_in = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        input_recordings: [],
        loaded: false,
        active_element: null,
        candidates: [],
        loaded_candidates: false,
        selected_candidate: null,
        can_submit: false,
        removed: 0
    },
    mounted: function() {
        this.getInputReport();
    },
    methods: {
        getInputReport: function() {
            this.$http.get('/api/input-report/')
                .then((response) => {
                    this.input_recordings = response.data;
                    this.loaded = true;
                })
        },
        getElementInfo: function(element) {
            if (this.active_element)
                this.active_element.isActive = false;
            this.active_element = element;
            if (this.selected_candidate)
                this.selected_candidate.deactivateElement();
            this.selected_candidate = null;
            this.can_submit = false;
            this.getCandidates();
        },
        getCandidates: function() {
            var el = this.active_element;
            var body = {
                'isrc': el.metadata.rec_isrc,
                'artist': el.metadata.rec_artist,
                'title': el.metadata.rec_title,
                'duration': el.metadata.rec_duration
            }
            this.$http.post('/api/get-candidates/', 
            {'params': body})
                .then((response) => {
                    this.candidates = response.data;
                    this.loaded_candidates = true;
                })
        },
        selectCandidate: function(element) {
            if (this.selected_candidate)
                this.selected_candidate.deactivateElement();
            this.selected_candidate = element;
            this.can_submit = true;
        },
        submitCandidate: function() {
            if (!this.selected_candidate)
                return;
            this.can_submit = false;
            this.selected_candidate = null;
            this.loaded_candidates = false;
            this.active_element.deactivateElement()
            this.active_element.show = false;
            this.removed++;
            this.active_element = null;
            this.candidates = [];                
        }
    }
});