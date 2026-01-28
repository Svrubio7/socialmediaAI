<template>
  <div>
    <!-- Hero Section -->
    <LandingHero />
    
    <!-- Stats Bar -->
    <LandingStats />
    
    <!-- Features Section -->
    <LandingFeatures />
    
    <!-- How It Works -->
    <LandingHowItWorks />
    
    <!-- FAQ Section -->
    <LandingFAQ />
    
    <!-- CTA Section -->
    <LandingCTA />
  </div>
</template>

<script setup lang="ts">
// Page meta
useSeoMeta({
  title: 'ElevoAI - Elevate Your Social Media with AI',
  description: 'AI-powered video analysis, strategy generation, and multi-platform publishing. Create viral content 10x faster with ElevoAI.',
  ogTitle: 'ElevoAI - Elevate Your Social Media with AI',
  ogDescription: 'AI-powered video analysis, strategy generation, and multi-platform publishing.',
  ogImage: '/og-image.png',
  twitterCard: 'summary_large_image',
})
</script>
