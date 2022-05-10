<template>
  <div v-if="localModel" class="mt-5">
    <div class="field">
      <a class="button is-pulled-right" @click="openPemrissionModal(null)">
        <span class="icon">
          <i class="fas fa-plus"></i>
        </span>
        <span>Add Permission</span>
      </a>
      <label class="label">Permissions</label>
    </div>

    <table class="table is-fullwidth is-hoverable permissions-table">
      <thead>
        <tr>
          <th>Action</th>
          <th>Action on Fields</th>
          <th>Actor</th>
        </tr>
      </thead>
      <tbody>
        <tr class="is-clickable" v-for="(p, i) in localModel" :key="stateName + '-p-t-p-r-' + i" @click="openPemrissionModal(i)">
          <td>{{p.action}}</td>
          <td>
            <div v-for="(f, j) in p.actionFields" :key="stateName + '-p-t-p-f-' + i + '-' + j">
              <span class="tag" >{{f}}</span>&nbsp;
            </div>
          </td>
          <td>
            <div v-for="(g, j) in p.groups" :key="stateName + '-p-t-p-g-' + i + '-' + j">
              <span class="tag" >{{g}}</span>&nbsp;
            </div>
            <div v-for="(o, j) in p.others" :key="stateName + '-p-t-p-o-' + i + '-' + j">
              <span class="tag" >{{o}}</span>&nbsp;
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <permission-modal :opened="permissionModal.opened" :model="permissionModal.model" :fields="fields" :index="permissionModal.index"
      @permission-modal-closed="onPemrissionModalClosed" @permission-modal-saved="onPemrissionModalSaved" @permission-modal-deleted="onPemrissionModalDeleted" />

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
      permissionModal: {
        opened: false,
        model: null,
        index: null
      },
    }
  },
  watch: {
    model: function (val) {
      this.setLocalModel()
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
          if (Array.isArray(localModel)) {
            this.localModel = localModel
          } else {
            this.localModel = []
          }
        }
      } else {
        this.localModel = []
      }
    },
    openPemrissionModal (index) {
      this.permissionModal.index = index
      if (index == null) {
        this.permissionModal.model = {
          action: 'View',
          actionFields: ['All'],
          groups: [],
          others: [],
        }
      } else {
        this.permissionModal.model = this.localModel[index]
      }
      this.permissionModal.opened = true
    },
    onPemrissionModalClosed () {
      this.permissionModal.opened = false
    },
    onPemrissionModalSaved (val) {
      var permission = JSON.parse(JSON.stringify(val))
      if (this.permissionModal.index == null) {
        var index = this.findPermissionIndex(permission.action)
        this.localModel.splice(index, 0, permission)
      } else {
        this.localModel.splice(this.permissionModal.index, 1, permission)
      }
      this.permissionModal.opened = false
    },
    onPemrissionModalDeleted () {
      this.localModel.splice(this.permissionModal.index, 1)
      this.permissionModal.opened = false
    },
    findPermissionIndex (action) {
      var lastIndexes = {'View': -1, 'Edit': -1, 'Delete': -1}
      for (var i=0;i<this.localModel.length;i++) {
        lastIndexes[this.localModel[i].action] = i
      }
      if (action == 'View') {
        if (lastIndexes['View'] != -1) {
          return lastIndexes['View'] + 1
        }
        return 0
      }
      if (action == 'Edit') {
        if (lastIndexes['Edit'] != -1) {
          return lastIndexes['Edit'] + 1
        }
        return lastIndexes['View'] + 1
      }
      return this.localModel.length
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
