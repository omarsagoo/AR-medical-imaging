db.createUser(
    {
        user:"omar",
        pwd: "password",
        roles: [
            {
                role: "readWrite",
                db: "medfiles"
            }
        ]
    }
)