<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">{{index == null ? 'New Row' : 'Edit Row'}}</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body" v-if="localModel">

        <div v-for="(c, i) in columns" :key="'sheet-row-modal-'+i">
          <string-field :name="c" :label="c" :value="localModel[c]" @value-changed="onValueChanged" />
        </div>

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link" @click="save">Save</a>
        <a class="button is-danger" @click="removeRow" v-if="index != null">Delete</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'

export default {
  name: 'sheet-row-modal',
  components: {
    StringField
  },
  props: ['opened', 'model', 'columns', 'index'],
  data () {
    return {
      localModel: null,
    }
  },
  computed: {
    
  },
  watch: {
    opened: function (val) {
      if (val) {
        this.localModel = JSON.parse(JSON.stringify(this.model))
      }
    },
  },
  methods: {
    close () {
      this.$emit('sheet-row-modal-closed')
    },
    save () {
      this.$emit('sheet-row-modal-saved', this.localModel)
    },
    removeRow () {
      this.$emit('sheet-row-modal-removed')
    },
    onValueChanged (val) {
      var name = val[0]
      var value = val[1]
      if (this.model[name] != value) {
        this.localModel[name] = value
      }
    },
  },
}
</script>

<style scoped>

</style>
