<template>
  <div>
    <p>Participant List</p>
    <div v-for="(participant, key) in participants" :key="key">
      <hr>
        <p>参加者ID：{{ participant.user }}</p>
        <p>参加者名：{{ participant.first_name }}</p>
        <p>参加者アイコン：{{ participant.icon }}</p>
      <hr>
    </div>
  </div>
</template>
<script>
export default {
  name: 'BaseParticipant',
  data() {
    return {
      participants: []
    }
  },
  mounted :function(){
    console.log('BaseParticipant execute' + this.$route.query.id)
    this.axios
      .get('api/events/' + this.$route.query.id + '/participants')
      .then(response => {this.participants = response.data})
      .catch(error => console.log(error))
  }
}
</script>