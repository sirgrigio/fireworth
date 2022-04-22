import { AccountingFormatPipe } from './accounting-format.pipe';

describe('AccountingFormatPipe', () => {
  it('create an instance', () => {
    const pipe = new AccountingFormatPipe();
    expect(pipe).toBeTruthy();
  });
});
