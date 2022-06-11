<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Move workflows</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body pb-6">

        <div class="field">
          <label class="label">Select the folder to move the {{workflows.length}} workflow(s) into</label>
          <div class="control">
            <folder-tree-node :folderId="configId" :sourceFolderId="folderId" />
          </div>
          <p class="help is-info">It may take a while to move many workflows.</p>
        </div>

        <div class="field" v-if="waiting">
          <label class="label">Finished: {{count}}</label>
          <div class="control">
            <progress class="progress is-link" :value="count" :max="workflows.length"></progress>
          </div>
        </div>

        <div v-if="error" class="notification is-danger is-light">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link"  :disabled="!selectedFolder" :class="{'is-loading': waiting, 'my-disabled-button': !selectedFolder}" @click="move">Move</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import FolderTreeNode from '@/components/modals/FolderTreeNode'

export default {
  name: 'move-workflow-modal',
  components: {
    FolderTreeNode
  },
  props: ['opened', 'folder', 'workflows'],
  data () {
    return {
      waiting: false,
      error: '',
      count: 0,
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    orgId () {
      return this.$route.params.orgId
    },
    configId () {
      return this.$route.params.configId
    },
    folderId () {
      return this.$route.params.folderId
    },
    orgWorkflowConfigs () {
      return this.$store.state.org.orgWorkflowConfigs
    },
    orgWorkflowConfig () {
      if (!this.orgWorkflowConfigs) {
        return null
      }
      for(const workflowConfig of this.orgWorkflowConfigs) {
        if (workflowConfig.id == this.configId) {
          return workflowConfig
        }
      }
      return null
    },
    folderMap () {
      return this.$store.state.folders.folderMap
    },
    selectedFolderId () {
      return this.$store.state.folders.selectedFolderId
    },
    selectedFolder () {
      if (this.folderMap && this.selectedFolderId) {
        return this.folderMap[this.selectedFolderId]
      }
      return null
    },
    selectedFolderPath () {
      if (!this.selectedFolder) {
        return ''
      }
      var parentId = this.selectedFolder.parentId
      var path = parentId ? this.selectedFolder.name : this.orgWorkflowConfig.name
      while (parentId) {
        var folder = this.folderMap[parentId]
        var parentId = folder.parentId
        path = (parentId ? folder.name : this.orgWorkflowConfig.name) + '/' + path
      }
      return path
    },
  },
  methods: {
    close () {
      this.$emit('move-workflow-modal-closed')
    },
    move () {
      if (this.waiting || !this.selectedFolder) {
        return
      }
      var confirm = {
        title: 'Move Workflow to Folder',
        message: 'Are you sure to move ' + this.workflows.length + ' workflows to the folder "' + this.selectedFolderPath + '"?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.moveConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    moveConfirmed () {
      this.waiting = true
      var promises = []
      for (const workflow of this.workflows) {
        var promise = this.$http.post(this.server + '/org/move-workflow/', {configId: this.configId, workflowId: workflow.id, folderId: this.selectedFolder.id}).then(resp => {
          this.count = this.count + 1
        }, err => {
          this.error = err
        })
        promises.push(promise)
      }
      var vm = this
      Promise.all(promises).then(success => {
        vm.waiting = false
        vm.$emit('move-workflow-modal-closed', true)
      }, err => {
        vm.error = 'Failed to move some workflows. Please refresh the page and try again.'
      })
    },
  },
}
</script>
