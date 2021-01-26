<template>
  <div>
    <p>Participant List</p>
    <div v-for="(participant, key) in participants" :key="key">
      <hr>
        <p>{{ participant.id }}</p>
        <p>{{ participant.name }}</p>
      <hr>
    </div>
    <button v-on:click="showAll">all</button>
    <p>{{ tmpMsg }}</p>
  </div>
</template>

<script>
export default {
  name: 'ParticipantList',
  data() {
    return {
      participants: [],
      tmpMsg: ""
    };
  },
  mounted :function() {
    this.axios
      .get('https://jsonplaceholder.typicode.com/users')
      .then(response => {this.participants = response.data})
      .catch(error => console.log(error))
  },
  methods: {
    showAll: function (){
      this.tmpMsg = "全参加者を見せます"
    }
  }
}
</script>


<style scoped>
</style>
