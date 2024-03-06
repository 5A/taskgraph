<template>
  <a-breadcrumb style="margin: 16px 0">
    <a-breadcrumb-item>Help</a-breadcrumb-item>
    <a-breadcrumb-item>Connection</a-breadcrumb-item>
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
      <a-typography-title :level="2">Connection Settings</a-typography-title>
      <a-typography-paragraph>
        [TODO] 
        
        a frontend-backend seperated application, which means one
        part of the application is only responsible for drawing and displaying
        User Interfaces, and the other part of the application is responsible to
        handle the actual logics to do stuff. The first part is called a
        frontend and is what you see here when you open this app, and the second
        part is called a backend, which is a server running remotely. For the
        frontend to be able to communicate with the backend and instruct the
        backend to do stuff, you must first tell the frontend where to find the
        remote backend. This can be done from the
        <a-typography-text strong>Control Panel - Connection</a-typography-text>
        panel.
      </a-typography-paragraph>
      <a-typography-paragraph>
        There're multiple methods a frontend can communicate with the backend,
        including HTTP requests, WebSocket connection, gRPC, and more. All these
        methods encapsulate command and other information in a special format
        and send the encapsulated package to a remote server on the same
        network. Different protocols fit different needs, and all of them can be
        used in one application.
      </a-typography-paragraph>
      <a-typography-title :level="3">RESTful Settings</a-typography-title>
      <a-typography-paragraph>
        The RESTful API is based on HTTP protocol. When calling the API, it is
        equivalent to accessing a website from a browser. Thus you are probably
        quite familier with the format of the address. The API address starts
        with https:// or https://, then followed by a domain name or an IP
        address, then followed by the port of the remote server, and finally an
        endpoint which is the route of the API on the server. The overall
        address looks like http://app.labctrl.org:8000/someAPI , and you can
        actually access the API directly from your browser if you only need to
        read some value.
      </a-typography-paragraph>
      <a-typography-paragraph>
        When all fields are filled, you can click on Test button to check if the
        remote server can be accessed from your location. In a complicated
        network, your request may need to go through several firewalls, WAFs and
        NATs to get to the target machine, thus an address working on one
        machine might not work on another. In that case, you will need to set up
        appropriate proxy or port mapping and Test it until you see the RESTful
        status icon becomes Online.
      </a-typography-paragraph>
      <a-typography-title :level="3">WebSocket Settings</a-typography-title>
      <a-typography-paragraph>
        WebSocket is similar to a real-time messenger app you use to chat with
        your friend. Both sides can send messages to each other and once you
        receive a message, you get notified immediately. So this protocol is
        useful when you need a faster or more synchronous control of the device.
        The API address starts with ws:// or wss://, then followed by a domain
        name or an IP address, then followed by the port of the remote server,
        and finally an endpoint which is the route of the API on the server. The
        overall address looks like ws://app.labctrl.org:8000/somews. You can use
        a websocket client to connect to such address if you want to play around
        with the API.
      </a-typography-paragraph>
      <a-typography-paragraph>
        Similar with above, when all fields are filled, you can click on Test
        button to check if the remote server can be accessed from your location
        and if the remote server is a websocket endpoint. In a complicated
        network, your request may need to go through several firewalls, WAFs and
        NATs to get to the target machine, thus an address working on one
        machine might not work on another. In that case, you will need to set up
        appropriate proxy or port mapping and Test it until you see the
        WebSocket status icon becomes Connected. The test connection will close
        itself shortly after the connection is established, thus you will see
        the status icon becomes Disconnected after it shows Connected. This
        means the remote server is ready and online. If the remote server is
        down or unreachable, the status icon will show a cross with "Error".
        Setting up a proxy for websocket requires more sophisticated techniques
        to handle interruptions and security correctly, thus we recommand using
        port mappings or VPN over proxy.
      </a-typography-paragraph>
      <a-typography-title :level="3">gRPC Settings</a-typography-title>
      <a-typography-paragraph>
        Most of our needs can be covered by combination of RESTful and WebSocket
        APIs. Thus only rarely will we need to setup gRPC. gPRC stands for
        google Remote Procedure Calls. Compared to RESTful API or WebSocket, it
        is more efficient and can move tons of data very quickly and with little
        delay between caller and the server. Its performance is better but it is
        also more complicated to setup. It is only used when we need to process
        a lot of data and not used here.
      </a-typography-paragraph>
      <a-typography-title :level="3">Import and Export</a-typography-title>
      <a-typography-paragraph>
        We automatically save all connection information you entered locally,
        and the next time you open this app, it is automatically loaded for you
        so that you don't need to enter again. This feature requires the
        localStorage feature to be enabled on your browser. If you are using
        normal browsers such as edge, safari, chrome, or packed electron app,
        then localStorage is typically enabled by default. You can check the
        setting by looking at the "Allow localStorage" section in the header of
        the Connection page.
      </a-typography-paragraph>
      <a-typography-paragraph>
        If you want to keep an extra copy of your settings as backup, or if you
        want to use the same settings in another browser or machine, you can
        click on the Export button to download current settings as a JSON file.
        You can also import settings from file into application by clicking the
        Import button, then your browser will pop up a file selection window,
        and you can choose the desired JSON file. You can directly modify values
        in the JSON file, because it is text-based and you can use any
        text-editor to edit the file. If the JSON file did not provide all
        required fields, then only those specified fields are updated according
        to the Imported file. If a malformed JSON file is imported, the
        importation is aborted and no change will be applied.
      </a-typography-paragraph>
    </a-typography>
  </a-layout-content>
</template>
