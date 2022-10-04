<template>
  <div v-if="localModel" class="mt-1">
    <div class="field">
      <button class="button is-pulled-right" @click="openItemFieldModal(null)">
        <span class="icon">
          <i class="fas fa-plus"></i>
        </span>
        <span>New Field</span>
      </button>
      <label class="label">Item Fields</label>
    </div>

    <table class="table is-fullwidth is-hoverable">
      <thead>
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>Label</th>
          <th>Type</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(f, i) in localModel" :key="'f-r-' + i" class="is-clickable" @click="openItemFieldModal(i)">
          <th>{{i + 1}}</th>
          <td>{{f.name}}</td>
          <td>{{f.label}}</td>
          <td>{{f.type}}</td>
        </tr>
      </tbody>
    </table>

    <item-field-modal :opened="itemFieldModal.opened" :field="itemFieldModal.field" :index="itemFieldModal.index" :linkedFromOptions="linkedFromOptions"
      @item-field-modal-saved="onItemFieldModalSaved" @item-field-modal-closed="onItemFieldModalClosed"
      @item-field-modal-deleted="onItemFieldModalDeleted" />

  </div>
</template>

<script>
import ItemFieldModal from '@/components/modals/ItemFieldModal'

export default {
  name: 'CustomItemFields',
  components: {
     ItemFieldModal
  },
  props: ['model', 'linkedFromOptions'],
  data () {
    return {
      localModel: [],
      itemFieldModal: {
        opened: false,
        field: null,
        index: null,
        linkedFromOptions: [],
      },
    }
  },

  watch: {
    model: function (val) {
      this.setLocalModel()
    },
    localModel: {
      handler (val) {
        this.$emit('model-changed', ['itemFields', this.localModel])
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
    openItemFieldModal (index) {
      this.itemFieldModal.index = index
      if (index != null) {
        this.itemFieldModal.field = this.localModel[index]
      } else {
        this.itemFieldModal.field = {
          name: '',
          label: '',
          type: 'string',
          options: null,
          showSum: false,
        }
      }
      this.itemFieldModal.opened = true
    },
    onItemFieldModalSaved (val) {
      var field = JSON.parse(JSON.stringify(val))
      if (this.itemFieldModal.index == null) {
        this.localModel.push(field)
      } else {
        this.localModel.splice(this.itemFieldModal.index, 1, field)
      }
      this.itemFieldModal.opened = false
    },
    onItemFieldModalClosed () {
      this.itemFieldModal.opened = false
    },
    onItemFieldModalDeleted () {
      this.localModel.splice(this.itemFieldModal.index, 1)
      this.itemFieldModal.opened = false
    },
  },
  mounted () {
    this.setLocalModel()
  },
}
</script>

<style scoped lang="scss">

</style>
