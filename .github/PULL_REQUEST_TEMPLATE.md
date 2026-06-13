## 변경 내용
<!-- 무엇을 바꿨는지 간략히 -->

## 변경 이유
<!-- 왜 이 변경이 필요한지 -->

## 관련 이슈
<!-- Closes #123 -->

## 테스트
- [ ] 단위 테스트 추가/수정 (`@ExtendWith(MockitoExtension.class)`)
- [ ] 웹 레이어 테스트 (`@WebMvcTest`)
- [ ] 통합 테스트 (`@SpringBootTest`)
- [ ] JaCoCo 커버리지 80%+ 확인 (`./mvnw verify`)

## 변경 유형
- [ ] feat: 새 기능
- [ ] fix: 버그 수정
- [ ] refactor: 기능 변경 없는 코드 개선
- [ ] docs: 문서 변경
- [ ] test: 테스트 추가/수정
- [ ] chore: 빌드/설정 변경
- [ ] perf: 성능 개선

## Spring Boot 체크리스트
- [ ] 생성자 주입 사용 (`@Autowired` 필드 주입 없음)
- [ ] `@Transactional` 서비스 레이어에만 적용
- [ ] 엔티티 직접 반환 없음 (DTO 변환)
- [ ] `@Valid` 검증 적용
- [ ] 하드코딩된 시크릿 없음
- [ ] N+1 쿼리 없음 (EAGER fetch 없음)
- [ ] 예외 처리 누락 없음 (swallowed exception 없음)
