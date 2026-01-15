<template>
  <div>
    <!-- Hero Section -->
    <section class="relative overflow-hidden">
      <!-- Background -->
      <div class="absolute inset-0 bg-gradient-to-b from-surface-950 via-surface-900/50 to-surface-950" />
      <div class="absolute top-20 left-1/4 w-[500px] h-[500px] bg-primary-500/20 rounded-full blur-[100px]" />
      <div class="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-accent-500/20 rounded-full blur-[100px]" />

      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
        <div class="text-center max-w-4xl mx-auto">
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-display font-bold text-balance animate-fade-in">
            <span class="gradient-text">AI-Powered</span> Social Media
            <br class="hidden sm:block" />
            Marketing Hub
          </h1>
          
          <p class="mt-6 text-lg sm:text-xl text-surface-400 max-w-2xl mx-auto animate-fade-in animate-delay-100">
            Analyze video patterns, generate winning strategies, create optimized content,
            and publish across platforms—all powered by AI.
          </p>

          <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in animate-delay-200">
            <NuxtLink to="/auth/register" class="btn-primary text-lg px-8 py-3">
              Start Free Trial
            </NuxtLink>
            <NuxtLink to="#features" class="btn-secondary text-lg px-8 py-3">
              Learn More
            </NuxtLink>
          </div>

          <!-- Stats -->
          <div class="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto animate-fade-in animate-delay-300">
            <div>
              <div class="text-3xl font-display font-bold gradient-text">10x</div>
              <div class="text-surface-500 text-sm mt-1">Faster Content Creation</div>
            </div>
            <div>
              <div class="text-3xl font-display font-bold gradient-text">4</div>
              <div class="text-surface-500 text-sm mt-1">Platforms Supported</div>
            </div>
            <div>
              <div class="text-3xl font-display font-bold gradient-text">AI</div>
              <div class="text-surface-500 text-sm mt-1">Pattern Analysis</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-24 bg-surface-900/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-display font-bold">
            Everything You Need to <span class="gradient-text">Dominate</span> Social Media
          </h2>
          <p class="mt-4 text-surface-400 max-w-2xl mx-auto">
            From pattern analysis to automated publishing, we've got you covered.
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="feature in features" :key="feature.title" class="card-hover">
            <div class="w-12 h-12 bg-gradient-to-br from-primary-500/20 to-accent-500/20 rounded-lg flex items-center justify-center mb-4">
              <span class="text-2xl">{{ feature.icon }}</span>
            </div>
            <h3 class="text-xl font-display font-semibold mb-2">{{ feature.title }}</h3>
            <p class="text-surface-400">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="card bg-gradient-to-br from-primary-900/50 to-accent-900/50 border-primary-700/50 text-center py-16">
          <h2 class="text-3xl sm:text-4xl font-display font-bold mb-4">
            Ready to Transform Your Content Strategy?
          </h2>
          <p class="text-surface-300 max-w-xl mx-auto mb-8">
            Join creators who are using AI to create better content, faster.
          </p>
          <NuxtLink to="/auth/register" class="btn-primary text-lg px-8 py-3">
            Get Started Free
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const features = [
  {
    icon: '🎯',
    title: 'Pattern Analysis',
    description: 'AI analyzes your videos to identify what makes content successful—hooks, pacing, cuts, and more.',
  },
  {
    icon: '📊',
    title: 'Strategy Generation',
    description: 'Get AI-generated marketing strategies tailored to your content patterns and target platforms.',
  },
  {
    icon: '📝',
    title: 'Script Creation',
    description: 'Receive detailed filming and editing scripts based on proven success patterns.',
  },
  {
    icon: '✂️',
    title: 'Auto Video Editing',
    description: 'Automatically apply patterns to create optimized video variations for each platform.',
  },
  {
    icon: '🚀',
    title: 'Multi-Platform Publishing',
    description: 'Publish to Instagram, TikTok, YouTube, and Facebook with one click.',
  },
  {
    icon: '📈',
    title: 'Performance Analytics',
    description: 'Track performance across platforms and watch your pattern scores improve over time.',
  },
]
</script>
