## Spider with GRPC

----

#### Please submit issue if you have any question or advice.

You can find all GRPC API from [proto file](protocol%2Fspider.proto).

----

#### Now this server support:

| function                              | support | note                                                                  |
|---------------------------------------|---------|-----------------------------------------------------------------------|
| Bing wallpapaer                       | ☑️      | Support both url and redirect type with both Chinese main land and US |
| Upload wallpaper to Tencent COS daily | ☑️      | You should setup your own Tencent Cloud config                        |
| Weibo Hot                             | ☑️      |                                                                       |
| Zhihu Hot                             | ☑️      |                                                                       |
| 36KR Hot                              | ☑️      |                                                                       |                              
| Wall Street News                      | ☑️      |                                                                       |
| ODaily News                           | ☑️      |                                                                       |
| CaiXin News                           | ☑️      |                                                                       |
| Latest Gold Price                     | ☑️      |                                                                       |
| Currency Exchange rate                | ☑️      |                                                                       |

微博热搜的突发爆点提醒可选启用，具体的事件规则、环境变量、持久化与上线核验见[微博突发爆点提醒运维说明](docs/weibo-breaking-alerts.md)。




