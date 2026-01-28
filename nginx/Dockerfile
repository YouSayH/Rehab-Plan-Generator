FROM nginx:alpine

# デフォルトの設定ファイルを削除
RUN rm /etc/nginx/conf.d/default.conf

# 作成した設定ファイルをコンテナ内の所定の位置にコピー
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

# (必要であれば) オフライン用ファイルをイメージに焼き込む場合
# COPY ../frontend/public/libs /usr/share/nginx/html/libs

CMD ["nginx", "-g", "daemon off;"]