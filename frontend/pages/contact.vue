<template>
  <div>
    <!-- Hero Section -->
    <section class="relative pt-16 pb-10 lg:pt-20 lg:pb-12">
      <!-- Background -->
      
      <div class="relative container-wide">
        <div class="max-w-2xl mx-auto text-center">
          <UiBadge variant="primary" class="mb-6">Contact</UiBadge>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-mono tracking-tight text-balance mb-4">
            Get in <span class="gradient-text">touch</span>
          </h1>
          <p class="text-lg text-surface-600 dark:text-surface-400 leading-relaxed font-mono">
            Have questions about ElevoAI? We'd love to hear from you.
          </p>
        </div>
      </div>
    </section>

    <!-- Contact Form -->
    <section class="py-6 md:py-8">
      <div class="container-wide">
        <!-- Divider -->
        <div class="section-divider mb-6" />
        
        <div class="grid lg:grid-cols-2 gap-12 lg:gap-16 max-w-5xl mx-auto">
          <!-- Form -->
          <div class="card p-8">
            <h2 class="text-xl font-mono text-surface-900 dark:text-surface-50 mb-6">Send us a message</h2>
            <form @submit.prevent="handleSubmit" class="space-y-5">
              <div class="grid sm:grid-cols-2 gap-5">
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
                <label class="label font-mono">Message</label>
                <textarea 
                  v-model="form.message"
                  class="input min-h-[120px] resize-none font-mono"
                  placeholder="How can we help you?"
                  rows="5"
                  required
                />
              </div>
              
              <UiButton type="submit" variant="accent" size="lg" full-width>
                <span class="font-mono">Send Message</span>
                <UiIcon name="Send" :size="18" />
              </UiButton>
            </form>
          </div>
          
          <!-- Contact Info -->
          <div class="space-y-8">
            <div>
              <h2 class="text-xl font-mono text-surface-900 dark:text-surface-50 mb-3">Contact Information</h2>
              <p class="text-surface-600 dark:text-surface-500 text-sm leading-relaxed font-mono">
                Reach out through any of these channels. We typically respond within 24 hours.
              </p>
            </div>
            
            <div class="space-y-5">
              <div class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-lg bg-primary-500/15 flex items-center justify-center flex-shrink-0">
                  <UiIcon name="Mail" :size="20" class="text-primary-400" />
                </div>
                <div>
                  <h3 class="font-mono text-surface-900 dark:text-surface-200 mb-1 text-sm">Email</h3>
                  <p class="text-surface-600 dark:text-surface-500 text-sm font-mono">hello@elevoai.com</p>
                </div>
              </div>
              
              <div class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-lg bg-accent-200/15 flex items-center justify-center flex-shrink-0">
                  <UiIcon name="MessageCircle" :size="20" class="text-accent-200" />
                </div>
                <div>
                  <h3 class="font-mono text-surface-900 dark:text-surface-200 mb-1 text-sm">Live Chat</h3>
                  <p class="text-surface-600 dark:text-surface-500 text-sm font-mono">Mon-Fri, 9am-6pm EST</p>
                </div>
              </div>
              
              <div class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-lg bg-emerald-500/15 flex items-center justify-center flex-shrink-0">
                  <UiIcon name="MapPin" :size="20" class="text-emerald-400" />
                </div>
                <div>
                  <h3 class="font-mono text-surface-900 dark:text-surface-200 mb-1 text-sm">Location</h3>
                  <p class="text-surface-600 dark:text-surface-500 text-sm font-mono">San Francisco, CA</p>
                </div>
              </div>
            </div>
            
            <!-- Social Links -->
            <div>
              <h3 class="font-mono text-surface-900 dark:text-surface-200 mb-3 text-sm">Follow Us</h3>
              <div class="flex items-center gap-2">
                <a href="#" class="p-2.5 rounded-lg bg-surface-200 dark:bg-surface-800 text-surface-600 dark:text-surface-500 hover:text-surface-900 dark:hover:text-surface-200 transition-colors">
                  <UiIcon name="Twitter" :size="18" />
                </a>
                <a href="#" class="p-2.5 rounded-lg bg-surface-200 dark:bg-surface-800 text-surface-600 dark:text-surface-500 hover:text-surface-900 dark:hover:text-surface-200 transition-colors">
                  <UiIcon name="Linkedin" :size="18" />
                </a>
                <a href="#" class="p-2.5 rounded-lg bg-surface-200 dark:bg-surface-800 text-surface-600 dark:text-surface-500 hover:text-surface-900 dark:hover:text-surface-200 transition-colors">
                  <UiIcon name="Github" :size="18" />
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Divider -->
        <div class="section-divider mt-6" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Contact Us - ElevoAI',
  description: 'Get in touch with the ElevoAI team.',
})

const form = reactive({
  name: '',
  email: '',
  company: '',
  message: '',
})

const handleSubmit = () => {
  console.log('Form submitted:', form)
}
</script>
