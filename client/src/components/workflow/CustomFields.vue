<template>
  <div v-if="localModel" class="mt-6">
    <div class="field">
      <button class="button is-pulled-right" @click="openNewCustomFieldModal">
        <span class="icon">
          <i class="fas fa-plus"></i>
        </span>
        <span>New Field</span>
      </button>
      <label class="label">Fields</label>
    </div>

    <table class="table is-fullwidth is-hoverable">
      <thead>
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>Label</th>
          <th>Type</th>
          <th>Options</th>
          <th>Dashboard</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(f, i) in localModel" :key="'f-r-' + i" class="is-clickable" @click="openCustomFieldModal(i)">
          <th>{{i + 1}}</th>
          <td>{{f.name}}</td>
          <td>{{f.label}}</td>
          <td>{{f.type}}</td>
          <td>
            <div v-if="f.options">
              <div v-if="Array.isArray(f.options)">
                <div v-for="(o, j) in f.options" :key="'f-r-' + i + '-' + j">
                  <span class="tag">
                    {{o}}
                  </span>
                </div>
              </div>
              <div v-else>
                <span class="icon">
                  <i class="fas fa-user-friends"></i>
                </span>
                <span>{{f.options}}</span>
              </div>
            </div>
          </td>
          <td>{{f.dashboard}}</td>
        </tr>
      </tbody>
    </table>

    <new-custom-field-modal :opened="newCustomFieldModal.opened" :insertOptions="newCustomFieldModal.insertOptions"
      @new-custom-field-modal-saved="onNewCustomFieldModalSaved" @new-custom-field-modal-closed="onNewCustomFieldModalClosed" />
    
    <custom-field-modal :opened="customFieldModal.opened" :field="customFieldModal.field" :index="customFieldModal.index"
      @custom-field-modal-saved="onCustomFieldModalSaved" @custom-field-modal-closed="onCustomFieldModalClosed"
      @custom-field-modal-deleted="onCustomFieldModalDeleted" />

  </div>
</template>

<script>
import NewCustomFieldModal from '@/components/modals/NewCustomFieldModal'
import CustomFieldModal from '@/components/modals/CustomFieldModal'

export default {
  name: 'CustomFields',
  components: {
    NewCustomFieldModal,
    CustomFieldModal
  },
  props: ['model'],
  data () {
    return {
      localModel: [],
      newCustomFieldModal: {
        insertOptions: [],
        opened: false
      },
      customFieldModal: {
        opened: false,
        field: null,
        index: null,
      },
    }
  },

  watch: {
    model: function (val) {
      this.setLocalModel()
    },
    localModel: {
      handler (val) {
        this.$emit('model-changed', ['fields', this.localModel])
      },
      deep: true
    },
  },
  methods: {
    setLocalModel () {
      var modelJson = JSON.stringify(this.model)
      var localModelJson = JSON.stringify(this.localModel)
      if (modelJson != localModelJson) {
        this.localModel = JSON.parse(modelJson)
      }
    },
    openNewCustomFieldModal () {
      var options = []
      for (var i=0;i<this.localModel.length;i++) {
        options.push({
          label: this.localModel[i].name,
          value: i
        })
      }
      this.newCustomFieldModal.insertOptions = options
      this.newCustomFieldModal.opened = true
    },
    onNewCustomFieldModalSaved (val) {
      this.localModel.splice(val[0] + 1, 0, JSON.parse(JSON.stringify(val[1])))
      this.newCustomFieldModal.opened = false
    },
    onNewCustomFieldModalClosed () {
      this.newCustomFieldModal.opened = false
    },
    openCustomFieldModal (i) {
      this.customFieldModal.field = this.localModel[i]
      this.customFieldModal.index = i
      this.customFieldModal.opened = true
    },
    onCustomFieldModalSaved (val) {
      this.localModel.splice(val[0], 1, JSON.parse(JSON.stringify(val[1])))
      this.customFieldModal.opened = false
    },
    onCustomFieldModalClosed () {
      this.customFieldModal.opened = false
    },
    onCustomFieldModalDeleted (val) {
      this.localModel.splice(val, 1)
      this.customFieldModal.opened = false
    },
  },
  mounted () {
    this.setLocalModel()
  },
}
</script>

<style scoped lang="scss">

</style>
