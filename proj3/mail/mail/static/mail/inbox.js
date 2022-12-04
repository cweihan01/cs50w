/* Manages the one-page email app when nav buttons are pressed */
document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


/* Posts email submission form to database after it has been submitted */
function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#message').innerHTML = '';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields when page is reloaded
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // POST form to API route '/emails', but do not submit
  document.querySelector('#compose-form').onsubmit = () => {
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Response from server:', data);
      if (data.error) {
        // Empty or invalid fields, throw error
        document.querySelector('#message').innerHTML = data.error;
        alert(data.error);
      } else {
        // Email sent successfully
        load_mailbox('sent');
        setTimeout(function(){ alert(data.message) }, 100);  
      }
    })

    // Prevent form from submitting
    return false;
  }
}


/* Loads either 'inbox', 'sent' or 'archive' mailboxes which display a list of respective emails */
function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#message').innerHTML = '';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  
  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
  // Request relevant emails in given mailbox via 'emails/<str:mailbox>' API route
  fetch(`emails/${mailbox}`)
  .then(response => response.json())
  .then(data => {
    
    // If for whatever reason user tries to access mail from an invalid mailbox, display error message
    // `data` will be an obj with `error` key
    if (data.error) {
      console.log(data.error);
      document.querySelector('#message').innerHTML = data.error;
    }

    // Display all emails in mailbox by requesting each email
    // `data` is now a list of `Email` objects
    console.log(`Mails in ${mailbox}:`, data);
    data.forEach(email => {

      // Create child elements for each email and fill with required info
      const senderElement = document.createElement('h5');
      const subjectElement = document.createElement('h6');
      const timestampElement = document.createElement('small');

      senderElement.innerHTML = email.sender;
      subjectElement.innerHTML = email.subject;
      timestampElement.innerHTML = email.timestamp;
      
      // Create a new emailDiv for each email and add child elements
      const emailDiv = document.createElement('div');
      emailDiv.id = email.id;
      emailDiv.className = 'email';
      if (email.read) {
        emailDiv.style.backgroundColor = 'white';
      } else {
        emailDiv.style.backgroundColor = '#D3D3D3';
      }
      emailDiv.innerHTML = senderElement.outerHTML + subjectElement.outerHTML + timestampElement.outerHTML;

      // Add event listener to each emailDiv - when user clicks, will be brought to that email
      emailDiv.addEventListener('click', () => load_email(email.id));
  
      // Add this email to mailbox view
      document.querySelector('#emails-view').appendChild(emailDiv);
    })
  })
}


/* Loads the page displaying a single email, once user clicks an email from any mailbox */
function load_email(email_id) {

  // Show email page and hide all other views
  document.querySelector('#message').innerHTML = '';
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#email-view').innerHTML = '';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Make GET request for email via 'emails/<int:email_id>' API route
  fetch(`emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    console.log('Email data fetched:', email);
    
    // Report any errors in finding email
    if (email.error) {
      console.log(error);
      message = document.querySelector('#message');
      message.innerHTML = error;
    }

    // Mark opened email as read
    fetch(`emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({
        read: true
      })
    })
    .then(response => {console.log('Marked email as read.')})

    // Create child info elements for each email
    const subject = document.createElement('h3');
    const sender = document.createElement('h5');
    const recipients = document.createElement('h6');
    const timestamp = document.createElement('small');
    const body = document.createElement('p');

    subject.innerHTML = email.subject;
    sender.innerHTML = email.sender;
    recipients.innerHTML = email.recipients.toString();
    timestamp.innerHTML = email.timestamp;
    body.innerHTML = email.body;

    // Add email info to div
    const emailBody = document.createElement('div');
    emailBody.innerHTML = subject.outerHTML + sender.outerHTML + recipients.outerHTML + timestamp.outerHTML + body.outerHTML;
    
    // Reply button
    const replyButton = document.createElement('button');
    replyButton.id = 'reply';
    replyButton.className = 'btn btn-primary btn-email';
    replyButton.innerHTML = 'Reply';
    replyButton.addEventListener('click', () => {

      // Load compose_email view
      compose_email();
      console.log('Replying to email...');
      
      // Pre-fill form based on original email
      document.querySelector('#compose-recipients').value = email.sender;
      document.querySelector('#compose-subject').value = 
        !email.subject.includes('Re:') ? 'Re: ' + email.subject : email.subject
      document.querySelector('#compose-body').value = `On ${email.timestamp}, ${email.sender} wrote: ${email.body}`
    })

    // Archive/Unarchive button
    const archiveButton = document.createElement('button');
    archiveButton.id = 'archive';
    archiveButton.className = 'btn btn-dark btn-email';
    archiveButton.innerHTML = email.archived ? 'Unarchive' : 'Archive';
    archiveButton.addEventListener('click', () => {
      fetch(`emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: !email.archived
        })
      })
      .then(response => {
        console.log(`Email ${!email.archived ? 'archived' : 'unarchived'}, returning to inbox.`);
        setTimeout(function() {load_mailbox('inbox')}, 100);
      })
    })

    // Add email text and buttons to email-view (which has only one email)
    document.querySelector('#email-view').appendChild(emailBody);
    document.querySelector('#email-view').appendChild(replyButton);
    document.querySelector('#email-view').appendChild(archiveButton);
  }) 
}