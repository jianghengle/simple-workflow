<template>
  <div class="mb-5">
    <div v-if="error" class="notification is-danger is-light">
      <button class="delete" @click="error=''"></button>
      {{error}}
    </div>
    <div v-if="waiting">
      <span class="icon is-medium is-size-4">
        <i class="fas fa-spinner fa-pulse"></i>
      </span>
    </div>
    <div v-if="url">
      <div class="mb-1">
        <button v-if="!readonly" class="delete mt-1 is-pulled-right" @click="deleteFile"></button>
        <a class="my-file-name" :href="url" :download="fileValue.filename">{{fileValue.filename}}</a>
      </div>
      <div v-if="!isImage && iframeSource">
        <iframe class="my-doc" :src="iframeSource"></iframe>
      </div>
      <div v-if="isImage" class="my-image-container">
        <img class="my-image" :src="url" />
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'file-display',
  props: ['fileValue', 'fileIndex', 'readonly'],
  data () {
    return {
      url: null,
      waiting: false,
      error: '',
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    isImage () {
      if (!this.fileValue) {
        return false
      }
      var ss = this.fileValue.filename.split('.')
      var ext = ss[ss.length - 1].toLowerCase()
      if (['png', 'jpg', 'jpeg', 'bmp', '.apng', 'gif'].includes(ext)) {
        return true
      }
      return false
    },
    iframeSource () {
      if (this.url) {
        var encodedUrl = encodeURIComponent(this.url);
        return "https://docs.google.com/gview?url=" + encodedUrl + "&embedded=true"
      }
    },
  },
  watch: {
    fileValue: function (val) {
      this.url = null
      if (val) {
        this.getS3DownloadUrl()
      }
    },
  },
  methods: {
    getS3DownloadUrl () {
      this.waiting = true
      this.$http.post(this.server + '/org/get-s3-download-url', this.fileValue).then(resp => {
        this.url = resp.body.url
        this.waiting = false
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
    deleteFile () {
      var confirm = {
        title: 'Delete File',
        message: 'Are you sure to delete this file?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.deleteFileConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    deleteFileConfirmed () {
      this.$emit('file-deleted', this.fileIndex)
    },
  },
  mounted () {
    if (this.fileValue) {
      this.getS3DownloadUrl()
    }
  },
}
</script>

<style lang="scss" scoped>
.my-file-name {
  text-decoration: underline;
  margin-right: 15px;
}

.my-doc {
  width: 100%;
  height: 600px;
}
.my-image-container {
  width: 100%;
  max-height: 600px;

  .my-image {
    max-height: 600px;
    max-width:100%;
  }
}
</style>
