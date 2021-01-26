<template>
  <div class="home">
    <router-link to="/create_update_event">create</router-link>
    <EventList />
  </div>
</template>

<script>
import EventList from '@/components/Event/EventList.vue'

export default {
  name: 'Home',
  components: {
    EventList
  }
}
</script>
