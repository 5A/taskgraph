<template>
  <a-breadcrumb style="margin: 16px 0">
    <a-breadcrumb-item>Help</a-breadcrumb-item>
    <a-breadcrumb-item>Authenticaiton</a-breadcrumb-item>
  </a-breadcrumb>
  <a-layout-content
    :style="{
      background: '#fff',
      padding: '24px',
      margin: 0,
      minHeight: '280px',
    }"
  >
    <a-typography>
      <a-typography-title :level="2">Authentication</a-typography-title>
      <a-typography-paragraph>
        [TODO]
        The authentication process must be designed
        carefully to prevent loopholes or weakness, thus the industrial standard
        OAuth2.0 authentication is employed by our server APIs.
      </a-typography-paragraph>
      <a-typography-paragraph>
        The device server uses something called a "Token" to check who has the
        authority to operate the devices. When a client tells the server to do
        some task, the client needs to send an Access Token alongside with the
        command. The server first validates the token, then if the token is
        valid, the server executes the command, and if the token is invalid, the
        server rejects the command and tell the client to use another token. The
        <a-typography-text strong>
          Control Panel - Authentication
        </a-typography-text>
        Page can be used to get new Access Tokens. This app can automatically
        send the tokens alongside with the commands for you, so to authenticate
        yourself, all you need to do is enter username and password in the
        Authentication page and click on Request New Token. The token is
        automatically stored locally, so the next time you open this app,
        there's no need to authenticate again unless the token has expired.
      </a-typography-paragraph>
      <a-typography-title :level="3">Access Token</a-typography-title>
      <a-typography-paragraph>
        The Token we use here is a "JSON Web Token", or JWT for short. It is a
        standardized form of access token which includes information such as
        expiration time, username, etc. in the token body. When the user wants
        to request a new token, the user sends his username and password in a
        url encoded form to the server. The server checks the username and
        password, and if correct, generates a JSON that includes the username,
        user id, expiration time and other information. Then the server
        serializes the JSON to a string that can be transmitted over HTTP, and
        the server signs the string with a secret key only known to the server.
        Finally, the server combines the string and the signature to form the
        JWT and sends the JWT to user.
      </a-typography-paragraph>
      <a-typography-paragraph>
        The JWT is not stored on the server. When a user provides a JWT to the
        server, the server can validate the JWT by looking at it's signature. If
        the signature is verified succesfully against the secret key stored on
        server, then the token is issued by the server and untempered. Then the
        server looks at the expiration time field in the token and compare the
        expiration time with local time to see if the token has expired.
      </a-typography-paragraph>
      <a-typography-paragraph>
        Overall, the token is like a temporary password given to the user by the
        server. So the user must store the token safely. If the token is stolen,
        it is equivalent to password being stolen before the token expires. Note
        that the token is also not encrypted except the signature part, so if
        the token is leaked, all information including username (but not
        password) is also leaked. This app automatically stores the new token
        requested in browser's localStorage, and it is not encrypted, so anyone
        using the computer can read the token. If you are using a public
        computer and do not want the token to be stored in the computer after
        session ends, you can click on Discard Token button before you leave the
        computer to delete the locally stored token. It is also possible to
        request a token on this app and use it in another program. In that case,
        uncheck the "Use this token to authenticate current application"
        checkbox and request a new token. The returned new token will not be
        used by this app to authenticate operations, but the token will be
        displayed in the card below the request button and you can copy & paste
        it to other app.
      </a-typography-paragraph>
      <a-typography-title :level="3">
        Reason to use tokens over password
      </a-typography-title>
      <a-typography-paragraph>
        Traditionally, passwords are used to authenticate clients to operate on
        devices. However, there're several major benefits of using token over
        password:
      </a-typography-paragraph>
      <a-typography-paragraph>
        <ul>
          <li>
            When using passwords, if the user doesn't want to input password
            every time the app reloads, the password must be stored locally.
            This increases the risk of system compromisation because if a hacker
            steals the password, he can use the password forever, and the
            password can be used to collide with other databases to compromise
            even more systems. But if a token is stolen, the hacker can only use
            the token before it expires, and the token does not include any
            information of the password, so the password is still safe.
          </li>
          <li>
            Passing around passwords is more susceptable to MITM attacks. When
            using token authentication, password is only passed once.
          </li>
          <li>
            The Authentication and Validation are seperated. The user
            authenticates once and use the credential everywhere, and no special
            facilities such as cookies (which is often disabled) are required.
          </li>
        </ul>
      </a-typography-paragraph>
    </a-typography>
  </a-layout-content>
</template>
