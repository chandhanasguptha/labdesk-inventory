# LabDesk

LabDesk is a small laboratory equipment checkout prototype. Students can browse available equipment and request a loan; staff can review requests and record returns. The project is a separate implementation inspired by the general laboratory inventory problem explored in [LabFlow](https://github.com/milan-kb/LabFlow), an MIT-licensed project by Milan K B. LabDesk does not include LabFlow source files.

The prototype was prepared with AI coding assistance; review and disclose that assistance according to course requirements.

## Features

- Equipment catalog with category and availability filters
- Student request workflow and request history
- Staff dashboard for approving requests and recording returns
- Express JSON API with optional MongoDB persistence
- Responsive React interface

## Run locally

Requires Node.js 20.19 or newer. From the project root:

```sh
pnpm install
pnpm dev
```

The client runs at `http://127.0.0.1:5173` and the API at `http://127.0.0.1:5000`.

To enable persistent MongoDB storage, copy `server/.env.example` to `server/.env` and set `MONGODB_URI`. Without it, the API uses demonstration data held in memory; changes reset when the server restarts.

## API

- `GET /api/health`
- `GET /api/equipment`
- `POST /api/equipment`
- `GET /api/requests`
- `POST /api/requests`
- `PATCH /api/requests/:id/status`

## Submission documents

- [Project report](output/pdf/LabDesk_Project_Report.pdf)
- [Software requirements specification](output/pdf/LabDesk_SRS.pdf)
- [Interface previews](output/pdf/LabDesk_Interface_Previews.pdf)

## Acknowledgement

The project theme and high-level workflow were informed by LabFlow, created by Milan K B. The code and interface in this repository were developed separately for LabDesk. See the upstream project and its MIT license at https://github.com/milan-kb/LabFlow.

## Limitations

This is a learning prototype. It does not implement user authentication, role enforcement, or production database provisioning. Do not enter real student or institution data. Production use requires authentication, authorization, audit logging, secure configuration, and a managed MongoDB deployment.
