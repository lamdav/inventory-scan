# Inventory Scan
## CLI to periodically check if a product is available for purchase

## Install
1. Install `poetry`
2. Run `poetry install`
3. Run `poetry shell`
4. Run `cp settings.yaml settings.local.yaml`
5. Modify the `setting.local.yaml`:
   - Update `scans` with store page url of what you want to track
   - Update `email` configuration if you want to be notified by email
   - Update `slack` configuration if you want to be notified in a slack workspace

## Usage
```shell
inv scan [--notifier/-n] (console|email|slack)
```

## Supported Stores
- Amazon
- BestBuy

## Supported Notifiers
- Console: Logs to the console item availability. Useful for debugging.
- Email: Uses email credentials to send bulk message to recipients.
  Highly recommend using an app password over your real account password.
- Slack: Send a slack message to a specific channel in a workspace.

## Extending Stores or Notifiers
> Q: I want to add another store front to be supported. How do I do that?

You will need to implement a `Handler` and pass it to the cli accordingly.
The `Handler` is responsible for parsing the `HTML` response of the store
page and extract pricing and availability information.

> Q: I want to be notified on {service}. How do I do that?

You will need to implement the `Notifier` interface and expose it to the
entrypoint accordingly along with passing in any constructor args from `settings.yaml`.
The `Notifier` is responsible for processing and grouping items as needed and
sending them upon scraping completion.
