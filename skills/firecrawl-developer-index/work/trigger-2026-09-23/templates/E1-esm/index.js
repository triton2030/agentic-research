const fetch = require('node-fetch');

async function main() {
  const res = await fetch('https://api.example.com/status');
  console.log(await res.json());
}

main();
