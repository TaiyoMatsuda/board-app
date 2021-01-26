<template>
  <div>
    <p>Event comment List</p>
    <div v-for="(eventcomment, key) in eventcomments" :key="key">
      <hr>
        <p>{{ eventcomment.id }}</p>
        <p>{{ eventcomment.name }}</p>
        <button v-on:click="deleteComment(key)">trash</button>
        <p>{{ deleteMsg }}</p>
      <hr>
    </div>
    <button v-on:click="showMoreComment">more</button>
    <p>{{ showMoreMsg }}</p>
  </div>
</template>

<script>
export default {
  name: 'EventCommentList',
  data() {
    return {
      eventcomments: [],
      deleteMsg: "",
      showMoreMsg: ""
    };
  },
  mounted :function() {
    this.axios
      .get('https://jsonplaceholder.typicode.com/users')
      .then(response => {this.eventcomments = response.data})
      .catch(error => console.log(error))
  },
  methods: {
    deleteComment: function (index){
      this.deleteMsg = this.eventcomments[index].id + "コメントを消します。"
    },
    showMoreComment: function (){
      this.showMoreMsg = "追加でコメントを表示します。"
    }
  }
}
</script>


<style scoped>
</style>
