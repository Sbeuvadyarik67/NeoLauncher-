# Changelog

Все значимые изменения проекта документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added
- (здесь будут новые фичи)

### Fixed
- (здесь будут исправления)

## [2.0.0] - 2026-09-12

### Added
- Лаунчер `NeoLauncher` с карточками проектов.
- Поддержка 4 проектов: NeoBrain, NeoSpace OS, NeoReceipt, Why Does This Exist?
- Переключение тем и стилей.
- Персонажи с учётом пола в NeoBrain.
- Плавная смена темы через overlay.
- Потоковый режим ответа AI.
- Кнопка остановки генерации.

### Fixed
- `base_dir`: `.exe` теперь находит `manifest.json` рядом с собой.
- Убран мусор из репозитория (`.gitignore`).
- Удалены личные настройки (`neobrain_settings.json`, `launcher_settings.json`) из репозитория.

### Changed
- Отказ от вшивания проектов в `.exe` — теперь проекты рядом, обновляются независимо.
- Переработана структура тем (10 тем + 5 стилей).

## [1.0.0] - 2026-06-01

### Added
- Первая версия `NeoBrain` (AI-чат на Ollama).
- Базовые проекты: NeoSpace OS, NeoReceipt, Why Does This Exist?
- Первый лаунчер.

[Unreleased]: https://github.com/Sbeuvadyarik67/NeoLauncher-/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/Sbeuvadyarik67/NeoLauncher-/releases/tag/v2.0.0
[1.0.0]: https://github.com/Sbeuvadyarik67/NeoLauncher-/releases/tag/v1.0.0