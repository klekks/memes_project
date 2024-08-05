# MemeStorage 
## Case for MADSOFT by Ilya Petrov

Meme Storage allows you to upload, store and delete memes with a text description.

## Build && Run

### Build
0. Install dependencies: ```sudo apt install git docker docker-compose```
1. Clone repo: ```git clone https://github.com/klekks/memes_project```
2. Build docker image: ```cd memes_progect && sudo docker-compose build```

### Run
3. Run project: ```sudo docker-compose up -d```
4. Check documentation of the API: [localhost/docs](http://localhost/docs)
5. Stop project: ```sudo docker-compose down --remove-orphans```

## Run tests
1. Run project: ```sudo docker-compose up -d```
2. Run MediaServiceTests ```sudo docker-compose exec media pytest .```
3. Run MemesServiceTests ```sudo docker-compose exec server pytest .```
4. Stop project: ```sudo docker-compose down --remove-orphans```


## Run in debug (dev) mode
To run in dev mode (all services will be available from the outside, docs in MediaService will be enabled) use following command:
```sudo docker-compose -f docker-compose-dev.yml up -d```

## limitations 
- All memes must be accompanied by text
- The text should not be empty
- Only jpeg, gif, png images are accepted
- The image size should not exceed 8 megabytes
