# Announcement API
This API is designed for a user to dynamically manage announcements for their websites.

## Add Announcement
Post an announcement using API

### Route:
`/announcement/post`

### Header:
| key    | value        |
|--------|--------------|
| APIKEY | Your api key |

### Request Body:
| key     | value                          |
|---------|--------------------------------|
| title   | The title of your announcement |
| domain  | The domain of your website     |
| content | The content of your website    |

### Request Parameters:
| key | value                                                                                              |
|-----|----------------------------------------------------------------------------------------------------|
| ttl | How long you want your announcement to last in the db. <br/>Announcements do not expire by default |


## Get Announcement
Get an announcement using API

### Route:
`/announcement/get`

### Request Parameters:
| key    | value                                        |
|--------|----------------------------------------------|
| domain | The domain of the announcement to be fetched |

## Delete Announcement
Delete an announcement using API

### Route:
`/announcement/delete`

### Header:
| key    | value        |
|--------|--------------|
| APIKEY | Your api key |

### Request Parameters:
| key    | value                                        |
|--------|----------------------------------------------|
| domain | The domain of the announcement to be fetched |