<template>
  <div class="event">
    <h1>This is an event page</h1>
    <Eventa />
  </div>
</template>

<script>
import Eventa from '@/components/Event.vue'

export default {
  name: 'Event',
  components: {
    Eventa
  }
}
</script>
