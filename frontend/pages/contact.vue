<template>
  <div>
    <!-- Hero Section -->
    <section class="relative overflow-hidden pt-32 pb-20 lg:pt-40 lg:pb-28">
      <!-- Background -->
      <div class="absolute inset-0 bg-surface-900" />
      <div class="absolute inset-0 bg-gradient-radial-top" />
      <div class="absolute top-1/3 right-1/3 w-[400px] h-[400px] bg-primary-500/8 rounded-full blur-[150px]" />
      
      <div class="relative container-wide">
        <div class="max-w-3xl mx-auto text-center">
          <UiBadge variant="primary" class="mb-6">Contact</UiBadge>
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-display font-bold tracking-tight text-balance mb-6">
            Get in <span class="gradient-text">Touch</span>
          </h1>
          <p class="text-xl text-surface-400 max-w-2xl mx-auto">
            Have questions about ElevoAI? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
          </p>
        </div>
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 section-divider" />
    </section>

    <!-- Contact Form -->
    <section class="section bg-surface-800/30 relative">
      <div class="absolute top-0 left-0 right-0 section-divider" />
      
      <div class="container-wide">
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-16">
          <!-- Form -->
          <UiCard class="p-8">
            <h2 class="text-2xl font-display font-bold text-surface-100 mb-6">Send us a message</h2>
            <form @submit.prevent="handleSubmit" class="space-y-6">
              <div class="grid sm:grid-cols-2 gap-6">
                <UiInput
                  v-model="form.name"
                  label="Name"
                  placeholder="Your name"
                  required
                />
                <UiInput
                  v-model="form.email"
                  label="Email"
                  type="email"
                  placeholder="you@company.com"
                  required
                />
              </div>
              
              <UiInput
                v-model="form.company"
                label="Company"
                placeholder="Your company name"
              />
              
              <div>
                <label class="label">Message</label>
                <textarea 
                  v-model="form.message"
                  class="input min-h-[140px] resize-none"
                  placeholder="How can we help you?"
                  rows="5"
                  required
                />
              </div>
              
              <UiButton type="submit" variant="accent" size="lg" full-width>
                <span>Send Message</span>
                <UiIcon name="Send" :size="18" />
              </UiButton>
            </form>
          </UiCard>
          
          <!-- Contact Info -->
          <div class="space-y-8">
            <div>
              <h2 class="text-2xl font-display font-bold text-surface-100 mb-4">Contact Information</h2>
              <p class="text-surface-400">
                Reach out to us through any of the following channels. Our team typically responds within 24 hours.
              </p>
            </div>
            
            <div class="space-y-6">
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 rounded-xl bg-primary-500/15 flex items-center justify-center flex-shrink-0">
                  <UiIcon name="Mail" :size="22" class="text-primary-400" />
                </div>
                <div>
                  <h3 class="font-semibold text-surface-100 mb-1">Email</h3>
                  <p class="text-surface-400">hello@elevoai.com</p>
                  <p class="text-surface-400">support@elevoai.com</p>
                </div>
              </div>
              
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 rounded-xl bg-accent-200/15 flex items-center justify-center flex-shrink-0">
                  <UiIcon name="MessageCircle" :size="22" class="text-accent-200" />
                </div>
                <div>
                  <h3 class="font-semibold text-surface-100 mb-1">Live Chat</h3>
                  <p class="text-surface-400">Available Mon-Fri, 9am-6pm EST</p>
                </div>
              </div>
              
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 rounded-xl bg-emerald-500/15 flex items-center justify-center flex-shrink-0">
                  <UiIcon name="MapPin" :size="22" class="text-emerald-400" />
                </div>
                <div>
                  <h3 class="font-semibold text-surface-100 mb-1">Location</h3>
                  <p class="text-surface-400">San Francisco, CA</p>
                  <p class="text-surface-400">United States</p>
                </div>
              </div>
            </div>
            
            <!-- Social Links -->
            <div>
              <h3 class="font-semibold text-surface-100 mb-4">Follow Us</h3>
              <div class="flex items-center gap-3">
                <a href="#" class="p-3 rounded-xl bg-surface-700 text-surface-400 hover:text-surface-100 hover:bg-surface-600 transition-colors">
                  <UiIcon name="Twitter" :size="20" />
                </a>
                <a href="#" class="p-3 rounded-xl bg-surface-700 text-surface-400 hover:text-surface-100 hover:bg-surface-600 transition-colors">
                  <UiIcon name="Linkedin" :size="20" />
                </a>
                <a href="#" class="p-3 rounded-xl bg-surface-700 text-surface-400 hover:text-surface-100 hover:bg-surface-600 transition-colors">
                  <UiIcon name="Github" :size="20" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="absolute bottom-0 left-0 right-0 section-divider" />
    </section>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Contact Us - ElevoAI',
  description: 'Get in touch with the ElevoAI team. We\'re here to help with any questions about our AI-powered marketing platform.',
})

const form = reactive({
  name: '',
  email: '',
  company: '',
  message: '',
})

const handleSubmit = () => {
  console.log('Form submitted:', form)
  // TODO: Implement form submission
}
</script>
