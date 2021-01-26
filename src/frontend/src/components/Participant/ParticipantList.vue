<template>
  <div>
    <p>Participant List</p>
    <div v-for="(participant, key) in participants" :key="key">
      <hr>
        <p>{{ participant.id }}</p>
        <p>{{ participant.name }}</p>
      <hr>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ParticipantList',
  data() {
    return {
      participants: []
    };
  },
  mounted :function(){
    this.axios
      .get('https://jsonplaceholder.typicode.com/users')
      .then(response => {this.participants = response.data})
      .catch(error => console.log(error))
  }
}
</script>


<style scoped>
</style>
