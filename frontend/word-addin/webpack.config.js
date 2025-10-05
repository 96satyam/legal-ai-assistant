const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

// Get certificates for HTTPS
const devCerts = require("office-addin-dev-certs");

module.exports = async (env, options) => {
  const dev = options.mode === "development";
  
  // Get HTTPS certificates
  const httpsOptions = await devCerts.getHttpsServerOptions();
  
  const config = {
    devtool: dev ? "source-map" : false,
    entry: {
      taskpane: "./src/taskpane/taskpane.js",
      commands: "./src/commands/commands.js"
    },
    output: {
      path: path.resolve(__dirname, "dist"),
      filename: "[name].bundle.js",
      clean: true
    },
    resolve: {
      extensions: [".js", ".jsx", ".json"]
    },
    module: {
  rules: [
    {
      test: /\.js$/,
      exclude: /node_modules/,
      use: {
        loader: "babel-loader",
        options: {
          presets: [
            ["@babel/preset-env", {
              targets: {
                ie: "11"
              },
              modules: false
            }]
          ]
        }
      }
    },
    {
      test: /\.html$/,
      use: ["html-loader"]
    },
    {
      test: /\.(png|jpg|jpeg|gif|svg)$/,
      type: "asset/resource",
      generator: {
        filename: "assets/[name][ext]"
      }
    }
  ]
},
    plugins: [
      new CleanWebpackPlugin(),
      new HtmlWebpackPlugin({
        template: "./src/taskpane/taskpane.html",
        filename: "taskpane.html",
        chunks: ["taskpane"]
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: "assets",
            to: "assets",
            noErrorOnMissing: true
          },
          {
            from: "manifest*.xml",
            to: "[name][ext]",
            transform(content) {
              if (dev) {
                return content;
              } else {
                return content.toString()
                  .replace(/https:\/\/localhost:3000/g, "YOUR_PRODUCTION_URL");
              }
            }
          }
        ]
      })
    ],
    devServer: {
      static: {
        directory: path.join(__dirname, "dist")
      },
      server: {
        type: "https",
        options: httpsOptions  // Use the certificates from office-addin-dev-certs
      },
      port: 3000,
      headers: {
        "Access-Control-Allow-Origin": "*"
      },
      hot: true,
      open: false
    }
  };

  return config;
};