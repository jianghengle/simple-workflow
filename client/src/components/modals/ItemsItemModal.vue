<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">{{index == null ? 'New Item' : 'Edit Item'}}</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body" v-if="localModel">

        <div v-for="(f, i) in itemFields" :key="'items-item-modal-'+i">
          <string-field v-if="f.type=='string'" :name="f.name" :label="f.label" :value="localModel[f.name]" @value-changed="onValueChanged" :options="f.optionValues" />
          <number-field v-if="f.type=='number'" :name="f.name" :label="f.label" :value="localModel[f.name]" @value-changed="onValueChanged" />
          <strings-field v-if="f.type=='strings'" :name="f.name" :label="f.label" :value="localModel[f.name]" @value-changed="onValueChanged" :options="f.optionValues" />
        </div>

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link" @click="save">Save</a>
        <a class="button is-danger" @click="removeItem" v-if="index != null">Delete</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'
import NumberField from '@/components/form/NumberField'
import StringsField from '@/components/form/StringsField'

export default {
  name: 'items-item-modal',
  components: {
    StringField,
    NumberField,
    StringsField
  },
  props: ['opened', 'model', 'fields', 'index', 'parentModel'],
  data () {
    return {
      localModel: null,
    }
  },
  computed: {
    orgUsers () {
      return this.$store.state.org.orgUsers
    },
    groups () {
      if (!this.orgUsers) {
        return {}
      }
      var groups = {'All': []}
      this.orgUsers.forEach(function(user) {
        groups['All'].push({value: user.email, label: user.username ? (user.username + ' <' + user.email + '>') : user.email})
        if (user.groups) {
          user.groups.forEach(function(g) {
            if (!groups[g]) {
              groups[g] = []
            }
            groups[g].push({value: user.email, label: user.username ? (user.username + ' <' + user.email + '>') : user.email})
          })
        }
      })
      return groups
    },
    itemFields () {
      var itemFields = []
      for (const f of this.fields) {
        var field = JSON.parse(JSON.stringify(f))
        if (field.options) {
          if (Array.isArray(field.options)) {
            field.optionValues = field.options
          } else if (typeof(field.options) == 'string') {
            field.optionValues = this.groups[field.options]
          } else {
            var v = this.parentModel[field.options.from]
            var mappings = {}
            mappings[v] = []
            for (const m of field.options.mappings) {
              mappings[m.from] = m.deprivedOptions
            }
            field.optionValues = mappings[v]
          }
        }
        itemFields.push(field)
      }
      return itemFields
    },
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
      this.$emit('items-item-modal-closed')
    },
    save () {
      this.$emit('items-item-modal-saved', this.localModel)
    },
    removeItem () {
      this.$emit('items-item-modal-removed')
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
