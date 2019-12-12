import trafaret as T

REGISTER_TRAFARET = T.Dict({
    T.Key('name'): T.String(min_length=3),
    T.Key('last_name'): T.String(min_length=3),
    T.Key('email'): T.Email,
    T.Key('password'): T.String(min_length=6),
})

LOGIN_TRAFARET = T.Dict({
    T.Key('email'): T.Email,
    T.Key('password'): T.String(min_length=6),
})
