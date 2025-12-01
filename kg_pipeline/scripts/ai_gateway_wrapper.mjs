#!/usr/bin/env node
/**
 * Node.js wrapper for Vercel AI SDK
 * Accepts JSON input via stdin, calls AI SDK, returns JSON via stdout
 */

import { generateText } from 'ai';
import 'dotenv/config';

async function main() {
  try {
    // Read input from stdin
    const input = await new Promise((resolve) => {
      let data = '';
      process.stdin.on('data', chunk => data += chunk);
      process.stdin.on('end', () => resolve(data));
    });

    const params = JSON.parse(input);
    
    // Call AI SDK
    const result = await generateText({
      model: params.model,
      prompt: params.prompt,
      temperature: params.temperature || 0.1,
      maxTokens: params.maxTokens || 2000,
    });

    // Output result as JSON
    const output = {
      text: result.text,
      usage: result.usage,
      finishReason: result.finishReason
    };

    console.log(JSON.stringify(output));
  } catch (error) {
    console.error(JSON.stringify({
      error: error.message,
      stack: error.stack
    }));
    process.exit(1);
  }
}

main();
