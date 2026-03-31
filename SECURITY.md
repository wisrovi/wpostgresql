# Security Policy

## Supported Versions

We currently support the following versions of wpostgresql:

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within wpostgresql, please send an email to [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com). All security vulnerabilities will be promptly addressed.

Please include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

## Security Best Practices

When using wpostgresql in your applications:

1. **Database Credentials**: Never commit database credentials to version control. Use environment variables or secure secret management.
2. **SQL Injection**: While wpostgresql uses parameterized queries, always validate and sanitize user input.
3. **Connection Security**: Use SSL/TLS for database connections in production.
4. **Least Privilege**: Use database users with minimal required permissions.

## Dependencies

We aim to keep dependencies minimal and up-to-date. Please report any security concerns with dependencies to [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com).
