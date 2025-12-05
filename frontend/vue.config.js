const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: [],
  publicPath: '/',  // Explicitly set public path
  // Configure dev server client to use secure WebSocket when served over HTTPS
  devServer: (function() {
    const host = process.env.WDS_HOST || process.env.HOST || '0.0.0.0';
    const port = process.env.WDS_PORT || process.env.PORT || 8080;
    const socketUrl = process.env.WDS_SOCKET_URL || `wss://${host}:${port}/ws`;

    return {
      host,
      port: parseInt(port),
      allowedHosts: 'all',
      client: {
        webSocketURL: socketUrl,
        overlay: true
      },
      hot: true
    };
  })(),
  configureWebpack: {
    resolve: {
      fallback: {
        "http": require.resolve("stream-http"),
        "https": require.resolve("https-browserify"),
        "util": require.resolve("util/"),
        "zlib": require.resolve("browserify-zlib"),
        "stream": require.resolve("stream-browserify"),
        "crypto": require.resolve("crypto-browserify"),
        "url": require.resolve("url/"),
        "assert": require.resolve("assert/"),
        "buffer": require.resolve("buffer/")
      }
    }
  }
})