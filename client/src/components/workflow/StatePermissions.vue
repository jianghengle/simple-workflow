<template>
  <div v-if="localModel" class="mt-5">
    <div class="field">
      <label class="label">Permissions</label>
    </div>

    <table class="table is-fullwidth is-hoverable permissions-table">
      <thead>
        <tr>
          <th>Action</th>
          <th>Groups</th>
          <th>Others</th>
        </tr>
      </thead>
      <tbody>
        <tr class="is-clickable" @click="openPemrissionModal('view')">
          <td>View</td>
          <td>
            <div v-for="(g, i) in localModel.view.groups" :key="stateName + '-p-t-v-g-' + i">
              <span class="tag" >{{g}}</span>
            </div>
          </td>
          <td>
            <div v-for="(o, i) in localModel.view.others" :key="stateName + '-p-t-v-o-' + i">
              <span class="tag" >{{o}}</span>
            </div>
          </td>
        </tr>
        <tr class="is-clickable" @click="openPemrissionModal('save')">
          <td>Save</td>
          <td>
            <div v-for="(g, i) in localModel.save.groups" :key="stateName + '-p-t-s-g-' + i">
              <span class="tag" >{{g}}</span>
            </div>
          </td>
          <td>
            <div v-for="(o, i) in localModel.save.others" :key="stateName + '-p-t-s-o-' + i">
              <span class="tag" >{{o}}</span>
            </div>
          </td>
        </tr>
        <tr class="is-clickable" @click="openPemrissionModal('delete')">
          <td>Delete</td>
          <td>
            <div v-for="(g, i) in localModel.delete.groups" :key="stateName + '-p-t-d-g-' + i">
              <span class="tag" >{{g}}</span>&nbsp;
            </div>
          </td>
          <td>
            <div v-for="(o, i) in localModel.delete.others" :key="stateName + '-p-t-d-o-' + i">
              <span class="tag" >{{o}}</span>&nbsp;
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <permission-modal :opened="permissionModal.opened" :model="permissionModal.model" :fields="fields"
      @permission-modal-closed="onPemrissionModalClosed" @permission-modal-saved="onPemrissionModalSaved" />

  </div>
</template>

<script>
import PermissionModal from '@/components/modals/PermissionModal'


export default {
  name: 'StatePermissions',
  components: {
    PermissionModal
  },
  props: ['model', 'fields', 'stateName'],
  data () {
    return {
      localModel: null,
      actions: ['view', 'save', 'delete'],
      permissionModal: {
        opened: false,
        model: null,
        type: null,
      },
    }
  },
  watch: {
    model: function (val) {
      if (val) {
        this.setLocalModel()
      }
    },
    localModel: {
      handler (val) {
        this.$emit('model-changed', ['permissions', this.localModel])
      },
      deep: true,
    }, 
  },
  methods: {
    setLocalModel () {
      if (this.model) {
        var modelJson = JSON.stringify(this.model)
        var localModelJson = JSON.stringify(this.localModel)
        if (modelJson != localModelJson) {
          var localModel = JSON.parse(modelJson)
          for (const a of this.actions) {
            if (!localModel[a]) {
              localModel[a] = {
                groups: ['All'],
                others: []
              }
            }
          }
          this.localModel = localModel
        }
      }
    },
    openPemrissionModal (type) {
      this.permissionModal.type = type
      this.permissionModal.model = this.localModel[type]
      this.permissionModal.opened = true
    },
    onPemrissionModalClosed () {
      this.permissionModal.opened = false
    },
    onPemrissionModalSaved (val) {
      this.localModel[this.permissionModal.type] = val
      this.permissionModal.opened = false
    },
  },
  mounted () {
    this.setLocalModel()
  },
}
</script>

<style scoped lang="scss">
.permissions-table {
  margin-top: -10px;
}
</style>
