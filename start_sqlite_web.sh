#!/usr/bin/expect

spawn sqlite_web -P 5000 -H 0.0.0.0 -p 5000 people.db
expect "Enter password:" {
    send "your_password\r"
}
interact
