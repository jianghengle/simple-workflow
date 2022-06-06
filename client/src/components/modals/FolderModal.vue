<template>
  <div class="modal"
      :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Folder</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body pb-6">

        <div v-if="error" class="notification is-danger is-light">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>

        <string-field :name="'folderName'" :label="'Folder Name'" :value="newName" @value-changed="onValueChanged" />

      </section>
      <footer class="modal-card-foot">
        <a class="button is-link"  :disabled="!nameChanged" :class="{'is-loading': waiting, 'my-disabled-button': !nameChanged}" @click="save">{{folder ? 'Update' : 'Create'}}</a>
        <a class="button is-danger" v-if="canDelete" :class="{'is-loading': waiting}" @click="deleteFolder">Delete</a>
        <a class="button" @click="close">Cancel</a>
      </footer>
    </div>
  </div>
</template>

<script>
import StringField from '@/components/form/StringField'

export default {
  name: 'folder-modal',
  components: {
    StringField
  },
  props: ['opened', 'folder', 'canDelete', 'parentId'],
  data () {
    return {
      newName: '',
      waiting: false,
      error: '',
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
    nameChanged () {
      if (this.folder) {
        return this.newName != this.folder.name
      }
      return this.newName
    },
  },
  watch: {
    opened: function (val) {
      if (val && this.folder && this.folder.name) {
        this.newName = this.folder.name
      }
    }
  },
  methods: {
    close () {
      this.$emit('folder-modal-closed')
    },
    onValueChanged (val) {
      this.newName = val[1]
    },
    save () {
      if (this.waiting || !this.nameChanged) {
        return
      }
      this.waiting = true
      if (this.folder) {
        var message = {
          id: this.folder.id,
          name: this.newName.trim(),
          workflowConfigId: this.configId,
        }
        this.$http.post(this.server + '/org/update-folder', message).then(resp => {
          this.$store.commit('folders/updateFolder', resp.body)
          this.waiting = false
          this.close()
        }, err => {
          this.error = err
          this.waiting = false
        })
      } else {
        var message = {
          name: this.newName.trim(),
          parentId: this.parentId,
          workflowConfigId: this.configId,
        }
        this.$http.post(this.server + '/org/create-folder', message).then(resp => {
          this.$store.commit('folders/addFolder', resp.body)
          this.waiting = false
          this.close()
        }, err => {
          this.error = err
          this.waiting = false
        })
      }   
    },
    deleteFolder () {
      if (this.waiting) {
        return
      }
      var confirm = {
        title: 'Delete Folder',
        message: 'Are you sure to delete this empty folder?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.deleteConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    deleteConfirmed () {
      this.waiting = true
      var message = {
        id: this.folder.id,
        workflowConfigId: this.configId,
      }
      this.$http.post(this.server + '/org/delete-folder', message).then(resp => {
        this.$store.commit('folders/removeFolder', this.folder.id)
        this.waiting = false
        this.$router.push('/org/' + this.orgId + '/workflow-folder/' + this.configId + '/' + this.folder.parentId)
        this.close()
      }, err => {
        this.error = err
        this.waiting = false
      })
    },
  },
}
</script>
